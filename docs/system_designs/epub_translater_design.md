# EPUB 翻译技术调研

主要涉及两点核心功能设计：
1. 读取并编辑 EPUB 文件
2. 使用 AI Agent 翻译 EPUB 文件

## EPUB 读取与编辑

基于智能体总结调研 Python 关于 EPUB 读取编辑的库(https://tiangong.cn/share/v2/doc/1943917081297530880?pid=1943912237641404416&sid=gen_doc-ycMNS37ix&t=gen_doc)，
决定使用 epubfile 来做 EPUB 书籍翻译

有点有以下几点：
1. 对 EPUB 的编辑改动范围小，可以只替换文字内容而不影响其他的部分
2. 提供完整文件 beautifulsoup ，灵活性高，方便后续灵活地使用 Agent 来翻译修改书籍文本


## AI Agent 翻译 EPUB 文本

技术栈使用 Agno Agent 框架

Agent 核心工作流：
1. 存储一个有状态的翻译术语表(glossary)
2. LLM 根据翻译术语表和待翻译文本翻译为目标语言
3. 将翻译后文本更新到 EPUB 文件中并保留原有样式等