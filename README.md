# ToolPageServer


内部用工具服务


Flask1.0的启动方式
此项改动应该是本次最大的变动了。

普通模式
传统的方式是在入口文件中写入app.run()，如果需要调试模式，则使用app.run(DEBUG=True)，最后使用python app.py运行主文件。

更新为1.0之后，启动方式改了
入口文件中无需写app.run().而是在环境变量中加入FLASK_APP=hello.py，FLASK_ENV=development,然后用命令python -m flask run即可启动服务。
