import os

import hydra
from dotenv import load_dotenv

from src.configs.eval_configs import EvalConfig


@hydra.main(config_path="../../configs", version_base="1.1")
def main(cfg: EvalConfig) -> None:
    os.environ["HYDRA_FULL_ERROR"] = "1"
    agent = hydra.utils.instantiate(cfg.agent)
    env = hydra.utils.instantiate(cfg.env)
    data_provider = hydra.utils.instantiate(cfg.data_src)


if __name__ == '__main__':
    load_dotenv()
    main()
