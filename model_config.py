class ModelConfig:
    def general_model_list(self) -> list:
        model_list = [
            "Qwen/Qwen2.5-72B-Instruct-128K",
            "deepseek-ai/DeepSeek-V2.5",
            "meta-llama/Meta-Llama-3.1-405B-Instruct",
            "Vendor-A/Qwen/Qwen2.5-72B-Instruct",
            "deepseek-ai/DeepSeek-Coder-V2-Instruct",
            "Qwen/Qwen2.5-Math-72B-Instruct",
            "google/gemma-2-27b-it",
            "yi-lightning"]
        return model_list
    
    def spider_model_list(self) -> list:
        model_list = [
            "Qwen/Qwen2.5-72B-Instruct-128K",
            "deepseek-ai/DeepSeek-V2.5",
            "meta-llama/Meta-Llama-3.1-405B-Instruct",
            "meta-llama/Meta-Llama-3.1-70B-Instruct"]
        return model_list
    
    def image_model_list(self) -> list:
        model_list = [
            "Qwen/Qwen2-VL-72B-Instruct",
            "OpenGVLab/InternVL2-Llama3-76B"]
        return model_list