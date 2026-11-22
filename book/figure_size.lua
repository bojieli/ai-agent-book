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
  end
  doc.blocks = blocks
  return doc
end
