import sys

import hydra
from omegaconf import DictConfig

# from source.finetune_ret import finetune
from source.generate import generate
from source.retrieve import retrieve


@hydra.main(version_base="1.3", config_path="configs", config_name="config")
def main(cfg: DictConfig):
    print(sys.path)

    if cfg.mode == "retrieve":
        print("test retrieval")

        retrieve(cfg.retrieve)

    elif cfg.mode == "generate":
        print("test inference")

        generate(cfg.generate)

    elif cfg.mode == "finetune":
        print("finetune retrieval")

        # finetune_ret(cfg.finetune_ret)


if __name__ == "__main__":
    main()
