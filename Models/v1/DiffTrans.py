import math
import torch
import torch.nn as nn
import torch.nn.functional as F

# --- helpers ---

class SinusoidalTimeEmbedding(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim
        self.proj = nn.Sequential(
            nn.Linear(dim, dim * 4),
            nn.SiLU(),
            nn.Linear(dim * 4, dim)
        )

    def forward(self, t):
        # t: (B,) in [0, 1] or [0, T)
        half = self.dim // 2
        freqs = torch.exp(
            torch.linspace(
                math.log(1e-4),
                math.log(1e4),
                half,
                device=t.device
            )
        )
        args = t[:, None] * freqs[None, :]
        emb = torch.cat([torch.sin(args), torch.cos(args)], dim=-1)
        if self.dim % 2 == 1:
            emb = F.pad(emb, (0, 1))
        return self.proj(emb)


class MLP(nn.Module):
    def __init__(self, dim, mlp_ratio=4.0):
        super().__init__()
        hidden = int(dim * mlp_ratio)
        self.fc1 = nn.Linear(dim, hidden)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(hidden, dim)

    def forward(self, x):
        return self.fc2(self.act(self.fc1(x)))


class DiTBlock(nn.Module):
    def __init__(self, dim, num_heads, mlp_ratio=4.0):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, num_heads, batch_first=True)
        self.norm2 = nn.LayerNorm(dim)
        self.mlp = MLP(dim, mlp_ratio)

        # FiLM‑style time conditioning
        self.time_mlp = nn.Sequential(
            nn.SiLU(),
            nn.Linear(dim, dim * 4)
        )

    def forward(self, x, t_emb):
        # x: (B, N, D), t_emb: (B, D)
        # time‑conditioning
        gamma_beta = self.time_mlp(t_emb)  # (B, 4D)
        gamma1, beta1, gamma2, beta2 = gamma_beta.chunk(4, dim=-1)

        # block 1: attention
        h = self.norm1(x)
        h = h * (1 + gamma1[:, None, :]) + beta1[:, None, :]
        attn_out, _ = self.attn(h, h, h)
        x = x + attn_out

        # block 2: MLP
        h = self.norm2(x)
        h = h * (1 + gamma2[:, None, :]) + beta2[:, None, :]
        x = x + self.mlp(h)
        return x


class DiT(nn.Module):
    def __init__(
        self,
        img_size=32,
        patch_size=1,
        in_channels=4,
        dim=1024,
        depth=16,
        num_heads=16,
        mlp_ratio=4.0,
        num_classes=None,
    ):
        super().__init__()
        self.img_size = img_size
        self.in_channels = in_channels
        self.num_patches = (img_size // patch_size) ** 2
        self.patch_dim = in_channels * patch_size * patch_size

        self.patch_embed = nn.Linear(self.patch_dim, dim)
        self.pos_embed = nn.Parameter(torch.zeros(1, self.num_patches, dim))

        self.time_embed = SinusoidalTimeEmbedding(dim)

        if num_classes is not None:
            self.label_embed = nn.Embedding(num_classes, dim)
        else:
            self.label_embed = None

        self.blocks = nn.ModuleList([
            DiTBlock(dim, num_heads, mlp_ratio)
            for _ in range(depth)
        ])
        self.norm = nn.LayerNorm(dim)
        self.head = nn.Linear(dim, self.patch_dim)

    def forward(self, x, t, y=None):
        """
        x: (B, C, H, W) latent
        t: (B,) timesteps (float or int)
        y: (B,) optional class labels
        """
        B, C, H, W = x.shape
        assert H == self.img_size and W == self.img_size

        # flatten to patches (here patch_size=1 for simplicity)
        x = x.view(B, C, H * W).permute(0, 2, 1)  # (B, N, C)
        x = self.patch_embed(x)                   # (B, N, D)
        x = x + self.pos_embed

        t_emb = self.time_embed(t)               # (B, D)

        if self.label_embed is not None and y is not None:
            y_emb = self.label_embed(y)          # (B, D)
            t_emb = t_emb + y_emb

        for blk in self.blocks:
            x = blk(x, t_emb)

        x = self.norm(x)
        x = self.head(x)                         # (B, N, patch_dim)
        x = x.permute(0, 2, 1).view(B, C, H, W)
        return x
