# 模型配置

运行项目时，会读取当前目录下的模型配置。

为了能使下载的模型能够被成功调用，你需要准备:

- \<model_filename\>.gguf - 模型文件
- \<model_filename\>.json - 模型运行配置参数文件

本项目提供了 `LFM-2.5-1.2B-Instruct` 模型的预配置文件。你可以直接下载模型文件并存放到 `model/` 文件夹中，然后直接启用 LFM 模型。

具体参数配置参考 (llama-cpp-python文档)[https://llama-cpp-python.readthedocs.io/en/latest/api-reference/#llama_cpp.Llama.__call__]，或者参考预配置文件进行修改。
