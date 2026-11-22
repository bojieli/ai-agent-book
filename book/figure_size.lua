function Image(el)
  el.attributes.width = "68%"
  el.attributes.height = "190mm"
  return el
end

-- Finish earlier body figures before the paragraph introducing the next one.
-- Figures inside an experiment box already stay in source order.
function Pandoc(doc)
  local blocks = pandoc.List()
  for i, block in ipairs(doc.blocks) do
    local following = doc.blocks[i + 1]
    if block.t == "Para" and following and following.t == "Figure" then
      blocks:insert(pandoc.RawBlock("latex", "\\FloatBarrier"))
    end
    blocks:insert(block)
    -- Finish the illustration before a table, or before the prose introducing a list.
    local sequence = doc.blocks[i + 2]
    local introduces_list = following and following.t == "Para" and sequence
      and (sequence.t == "BulletList" or sequence.t == "OrderedList")
    if block.t == "Figure" and following and (following.t == "Table" or introduces_list) then
      blocks:insert(pandoc.RawBlock("latex", "\\FloatBarrier"))
    end
  end
  doc.blocks = blocks
  return doc
end
