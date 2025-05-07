import os
import torch
from hydra import initialize_config_dir, compose
from hydra.core.global_hydra import GlobalHydra
from sam2.build_sam import build_sam2
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
# Paths
cfg_dir_rel = os.path.join("..","sam2","sam2","configs")
checkpoint  = os.path.join("..","sam2","checkpoints","sam2.1_hiera_tiny.pt")
cfg_name    = "sam2.1/sam2.1_hiera_t"

cfg_dir = os.path.abspath(cfg_dir_rel)
ckpt    = os.path.abspath(checkpoint)
assert os.path.isdir(cfg_dir),  f"Missing config dir: {cfg_dir}"
assert os.path.isfile(ckpt),    f"Missing checkpoint: {ckpt}"

# Pick device
if torch.backends.mps.is_available() and torch.backends.mps.is_built():
    device = "mps"
else:
    device = "cpu"
print("Using device:", device)

# Initialize Hydra
GlobalHydra.instance().clear()
with initialize_config_dir(config_dir=cfg_dir, version_base="1.1"):
    # pass the config‐name so build_sam2 can re‐compose under this Hydra context
    model = build_sam2(cfg_name, ckpt, device=device)

    mask_generater = SAM2AutomaticMaskGenerator(model)