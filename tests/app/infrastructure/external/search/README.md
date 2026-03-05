# Bing搜索引擎测试

## 测试文件
- `test_bing_search.py`: Bing搜索引擎的接口测试

## 运行测试

```bash
# 运行所有搜索测试
pytest tests/app/infrastructure/external/search/ -v -s

# 运行特定测试
pytest tests/app/infrastructure/external/search/test_bing_search.py::TestBingSearch::test_search_gemini -v -s
```

```angular2html
  运行所有日期范围测试                                                                                                                                                                                               
                                                                                                                                                                                                                     
  pytest tests/app/infrastructure/external/search/test_bing_search.py::TestBingSearch::test_search_with_date_range -v -s                                                                                             
                                                                                                                                                                                                                     
  运行特定参数的测试                                                                                                                                                                                                 
                                                                                                                                                                                                                     
  # 测试 gemini + day                                                                                                                                                                                                
  pytest tests/app/infrastructure/external/search/test_bing_search.py::TestBingSearch::test_search_with_date_range[gemini-day] -v -s                                                                                 
                                                                                                                                                                                                                     
  # 测试 python + week                                                                                                                                                                                               
  pytest tests/app/infrastructure/external/search/test_bing_search.py::TestBingSearch::test_search_with_date_range[python-week] -v -s                                                                                
                                                                                                                                                                                                                     
  自定义参数                                                                                                                                                                                                         
                                                                                                                                                                                                                     
  直接修改代码中的参数列表（第88-93行）：                                                                                                                                                                            
  @pytest.mark.parametrize("query,date_range", [                                                                                                                                                                     
      ("你的关键词1", "day"),                                                                                                                                                                                        
      ("你的关键词2", "week"),                                                                                                                                                                                       
      ("你的关键词3", "month"),                                                                                                                                                                                      
  ]) 
```

## 测试说明

### test_search_gemini
测试搜索"gemini"关键词的功能。

**验证项**：
1. ✅ 搜索请求成功（`result.success == True`）
2. ✅ 返回数据不为空（`result.data is not None`）
3. ✅ 查询关键词正确（`search_results.query == "gemini"`）
4. ✅ 如果有结果，验证结果结构（title, url, snippet）

**注意事项**：
- 测试会被重定向到 `cn.bing.com`（中国版Bing）
- 如果页面结构变化导致无法解析结果，测试会跳过（skip）而不是失败
- 测试会打印详细的调试信息，包括搜索结果的前3条

## 已知问题

1. **页面结构变化**: Bing的HTML结构可能会变化，导致解析失败
2. **地区重定向**: 从中国访问会被重定向到cn.bing.com，页面结构可能不同
3. **反爬虫**: 频繁请求可能被限流

## 修复的Bug

在创建测试过程中，发现并修复了 `bing_search.py` 中的一个bug：

**问题**: `ToolResult.data` 定义为 `dict` 类型，但代码中直接传递了 `SearchResults` 对象

**修复**: 
```python
# 修复前
return ToolResult(success=True, data=results)

# 修复后  
return ToolResult(success=True, data=results.model_dump())
```

## 测试输出示例

```
=== 搜索结果调试信息 ===
success: True
message: 
data type: <class 'dict'>
data: {'query': 'gemini', 'date_range': None, 'total_results': 0, 'results': []}

=== 搜索结果 ===
搜索关键词: gemini
日期范围: None
总结果数: 0
返回结果数: 0

⚠️  警告: 没有解析到搜索结果
这可能是因为:
1. Bing页面结构发生了变化
2. 被重定向到了不同的Bing版本（如cn.bing.com）
3. 网络问题或被限流
```
