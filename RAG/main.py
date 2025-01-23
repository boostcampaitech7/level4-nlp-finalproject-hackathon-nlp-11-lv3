import os
import sys

import hydra
from dotenv import load_dotenv
from omegaconf import DictConfig

# from source.finetune_ret import finetune
from source.generate import generate
from source.retrieve import retrieve


@hydra.main(version_base="1.3", config_path="configs", config_name="config")
def main(cfg: DictConfig):
    print(sys.path)
    load_dotenv()
    cfg.openai_key = os.getenv("OPENAI_API_KEY")

    if cfg.mode == "retrieve":
        print("test retrieval")

        retrieve(cfg)

    elif cfg.mode == "generate":
        print("test inference")

        generate(cfg)

    elif cfg.mode == "finetune":
        print("finetune retrieval")

        # finetune_ret(cfg)


if __name__ == "__main__":
    main()
