-- crossref.lua — номын дотоод эшлэл, холбоос (англи хэвлэл).
--
-- Одоогийн гараар өгсөн дугаарыг (Зураг N-M, Бүлэг N) хадгалж, текст дэх
-- эшлэл бүрийг товшиж болох дотоод холбоос болгож, зураг ба бүлэг бүрд
-- \label зангуу нэмнэ. LaTeX-ийн \label / \hyperref-ийг шууд ашиглах тул
-- LaTeX-ийн тоолуураас хамаарахгүй (харагдах текст нь гараар өгсөн дугаар хэвээр).
--
-- Хятад хэвлэлээс (图N-M нь нэг Str Token) ялгаатай нь англи
-- эшлэл Str("Figure") Space Str("2-6") гэсэн хоёр inline элементээс бүрдэнэ.
-- Иймээс Inlines түвшинд түлхүүр үгийн Token-ийг дараагийн тоон
-- Token-той нь хослуулан тааруулна.
--
-- Дээрээс доош дамжихдаа Image/Figure өөрийн тайлбарыг алгасахын тулд `false`
-- буцаана. Ингэснээр тайлбарт зангуу тавих ч өөр лүү нь холбоос үүсгэхгүй.

local chap = 0

local function fig_label(n, m) return 'fig:' .. n .. '-' .. m end
local function chap_label(n) return 'chap:' .. n end

-- ASCII үсэг/тоог байтын түвшинд шалгана (Lua-ийн %w нь орчноос хамаарч
-- UTF-8 үргэлжлэлийн байтыг тахир хашилт, урт зураастай андуурч магадгүй).
local function is_ascii_alnum(b)
  return (b >= 48 and b <= 57) or (b >= 65 and b <= 90) or (b >= 97 and b <= 122)
end

-- Тооны дараах Str төгсгөлийг зөвшөөрнө: үсэг, тоо, зураасаар эхлээгүй
-- бүх зүйл (цэг тэмдэг, урт зураас, "'s", хаах хашилт/хаалт гэх мэт).
local function ok_suffix(s)
  if s == '' then return true end
  local b = s:byte(1)
  return not (is_ascii_alnum(b) or b == 45)  -- 45 = '-'
end

-- "…Figure" / "…Chapter" Token-ийг хуваана: түлхүүр үгийн өмнө залгаатай
-- цэг тэмдэг ASCII эсвэл олон байттай байж болно ("(Figure", "basics—Chapter").
-- Token түлхүүр үгээр төгсөөгүй эсвэл угтвар нь үсэг/тоогоор төгссөн
-- (жишээ нь "subChapter") бол nil, үгүй бол угтварыг буцаана.
local function split_kw(text, kw)
  local pre = text:match('^(.-)' .. kw .. '$')
  if not pre then return nil end
  if pre ~= '' and is_ascii_alnum(pre:byte(#pre)) then return nil end
  return pre
end

return {
  {
    traverse = 'topdown',

    Header = function(el)
      if el.level == 1 and not el.classes:includes('unnumbered') then
        chap = chap + 1
        el.content:insert(pandoc.RawInline('latex', '\\label{' .. chap_label(chap) .. '}'))
      end
      return el
    end,

    -- pandoc 3.x: дан зураг нь тайлбарыг агуулдаг Figure блок болно.
    Figure = function(el)
      local cap = pandoc.utils.stringify(el.caption.long)
      local n, m = cap:match('Figure%s*(%d+)%-(%d+)')
      if n and m then
        el.identifier = fig_label(n, m)  -- LaTeX бичигч \label{fig:N-M} үүсгэнэ
      end
      return el, false  -- тайлбар руу орохгүй (өөр лүү нь холбоос хийхгүй)
    end,

    -- Өөрийн тайлбартай хэвээр үлдсэн inline зурагт зориулсан нөөц арга.
    Image = function(el)
      local cap = pandoc.utils.stringify(el.caption)
      local n, m = cap:match('Figure%s*(%d+)%-(%d+)')
      if n and m and el.identifier == '' then
        el.identifier = fig_label(n, m)
      end
      return el, false
    end,

    Inlines = function(inlines)
      local out = pandoc.Inlines{}
      local i = 1
      local n = #inlines
      local changed = false
      while i <= n do
        local el = inlines[i]
        local linked = false
        if el.t == 'Str' and i + 2 <= n
            and inlines[i + 1].t == 'Space' and inlines[i + 2].t == 'Str' then
          local kind = 'Figure'
          local pre = split_kw(el.text, 'Figure')
          if not pre then
            kind = 'Chapter'
            pre = split_kw(el.text, 'Chapter')
          end
          if pre then
            local numtext = inlines[i + 2].text
            if kind == 'Figure' then
              local a, b, suffix = numtext:match('^(%d+)%-(%d+)(.*)$')
              if a and ok_suffix(suffix) then
                if pre ~= '' then out:insert(pandoc.Str(pre)) end
                out:insert(pandoc.RawInline('latex',
                  '\\crossreflink{' .. fig_label(a, b) .. '}{Figure ' .. a .. '-' .. b .. '}'))
                if suffix ~= '' then out:insert(pandoc.Str(suffix)) end
                linked = true
              end
            else
              local a, suffix = numtext:match('^(%d+)(.*)$')
              if a and ok_suffix(suffix) then
                if pre ~= '' then out:insert(pandoc.Str(pre)) end
                out:insert(pandoc.RawInline('latex',
                  '\\crossreflink{' .. chap_label(a) .. '}{Chapter ' .. a .. '}'))
                if suffix ~= '' then out:insert(pandoc.Str(suffix)) end
                linked = true
              end
            end
          end
        end
        if linked then
          i = i + 3
          changed = true
        else
          out:insert(el)
          i = i + 1
        end
      end
      if changed then return out end
    end,
  }
}
