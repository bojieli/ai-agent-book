-- Give every PDF table explicit column widths so prose wraps within the page.
-- CJK characters count as two Latin characters; square-root weights keep a
-- single long explanation from squeezing short labels into unreadable columns.
function Table(el)
  if not FORMAT:match('latex') then return el end
  local n = el.colspecs and #el.colspecs or #el.widths
  local widths = {}
  for i = 1, n do widths[i] = 4 end
  local function measure(rows)
    for _, row in ipairs(rows) do
      local column = 1
      for _, cell in ipairs(row.cells) do
        local text = pandoc.utils.stringify(cell.contents)
        local length = 0
        for _, code in utf8.codes(text) do
          length = length + (code > 255 and 2 or 1)
        end
        local span = cell.col_span or 1
        for i = column, math.min(n, column + span - 1) do
          widths[i] = math.max(widths[i], math.min(80, length / span))
        end
        column = column + span
      end
    end
  end
  if el.colspecs then
    measure(el.head.rows)
    for _, body in ipairs(el.bodies) do
      measure(body.head)
      measure(body.body)
    end
    measure(el.foot.rows)
  else
    -- Pandoc 2.9 represents tables as headers / rows / widths.
    local function old_row(cells)
      local row = {cells = {}}
      for _, blocks in ipairs(cells) do
        table.insert(row.cells, {contents = blocks, col_span = 1})
      end
      return row
    end
    measure({old_row(el.headers)})
    for _, row in ipairs(el.rows) do measure({old_row(row)}) end
  end
  local total = 0
  for i = 1, n do
    widths[i] = math.sqrt(widths[i])
    total = total + widths[i]
  end
  for i = 1, n do
    if el.colspecs then el.colspecs[i][2] = widths[i] / total
    else el.widths[i] = widths[i] / total end
  end
  return el
end

-- Attach manually numbered table titles to the table, keeping them on the
-- same page as its first row. Markdown and HTML source stay unchanged.
function Blocks(blocks)
  if not FORMAT:match('latex') then return blocks end
  local out = pandoc.List()
  local i = 1
  while i <= #blocks do
    local block = blocks[i]
    local next_block = blocks[i + 1]
    if block.t == 'Para' and next_block and next_block.t == 'Table'
      and pandoc.utils.stringify(block):match('^表%s*%d+%-%d+%s') then
      if next_block.colspecs then
        next_block.caption.long = {block}
      else
        next_block.caption = block.content
      end
      out:insert(next_block)
      i = i + 2
    else
      out:insert(block)
      i = i + 1
    end
  end
  return out
end
