# Semantic Document and Chunk IDs

## Overview

The contextual retrieval system now uses semantically meaningful document IDs based on file names instead of opaque MD5 hashes. This makes the system more transparent, debuggable, and user-friendly.

## ID Generation Rules

### Document ID
Generated from the file name with these transformations:
1. Remove file extension (.md)
2. Replace Chinese parentheses （） with underscores
3. Replace English parentheses () with underscores
4. Replace spaces and hyphens with underscores
5. Remove trailing underscores
6. Truncate to 100 characters if needed

### Chunk ID
Format: `{document_id}_chunk_{index}`
- Document ID as base
- Sequential chunk index (0, 1, 2...)

## Examples

| Original File | Document ID | Sample Chunk IDs |
|--------------|-------------|------------------|
| 宪法.md | 宪法 | 宪法_chunk_0, 宪法_chunk_1 |
| 劳动法（2018-12-29）.md | 劳动法_2018_12_29 | 劳动法_2018_12_29_chunk_0 |
| 民法典总则编.md | 民法典总则编 | 民法典总则编_chunk_0 |
| 检察官法（2019-04-23）.md | 检察官法_2019_04_23 | 检察官法_2019_04_23_chunk_0 |

## Comparison with Hash-Based IDs

### Old System (MD5 Hash)
```
Document: 08f758bf19c0
Chunks: 08f758bf19c0_chunk_0, 08f758bf19c0_chunk_1
```
- ❌ Not human-readable
- ❌ No semantic meaning
- ❌ Hard to debug
- ❌ Can't identify source document

### New System (Semantic)
```
Document: 宪法
Chunks: 宪法_chunk_0, 宪法_chunk_1
```
- ✅ Human-readable
- ✅ Self-documenting
- ✅ Easy to debug
- ✅ Clear source identification

## Benefits

1. **Transparency**: Users and developers can immediately identify which document a chunk comes from
2. **Searchability**: Can grep/search for specific laws by name in logs and data
3. **Debugging**: Easier to trace issues back to source documents
4. **Consistency**: Same document always generates the same ID
5. **Sortability**: Documents sort alphabetically by name

## Implementation

The ID generation is handled by the `generate_document_id()` method in `index_local_laws_contextual.py`:

```python
def generate_document_id(self, doc_info: Dict[str, Any]) -> str:
    """Generate a semantically meaningful document ID from file name."""
    base_name = doc_info["name"]
    
    # Clean up the name
    clean_name = base_name.replace('（', '_').replace('）', '')
    clean_name = clean_name.replace('(', '_').replace(')', '')
    clean_name = re.sub(r'[\s\-]+', '_', clean_name)
    clean_name = clean_name.strip('_')
    
    return clean_name
```

## Testing

Run the test script to see examples:
```bash
python test_document_ids.py
```

## Migration Note

If you have existing indexed documents with hash-based IDs, you'll need to re-index them to use the new semantic IDs:

```bash
python index_local_laws_contextual.py
```

## Future Enhancements

Potential improvements for the ID generation:
1. Add version tracking (e.g., 劳动法_v2018_12_29)
2. Include document type prefix (e.g., law_劳动法, regulation_xxx)
3. Support for hierarchical documents (e.g., 民法典/总则编 → 民法典_总则编)
