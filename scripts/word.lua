-- Filtro usato da scripts/converti_word.py per ripulire il testo che
-- Pandoc legge da una bozza di Word (.docx) e adattarlo al sito.
--
-- Stili di paragrafo di Word riconosciuti:
--   "Regesto"         -> riquadro richiudibile (il primo paragrafo è il titolo)
--   "Nota a margine"  -> nota a margine
--   "Didascalia"      -> didascalia dell'immagine che la precede
--   "Citazione"       -> citazione rientrata
-- Tutti gli altri stili personalizzati vengono ignorati (resta il testo).

local function stile(el)
  local s = el.attributes and el.attributes["custom-style"]
  if not s then return nil end
  return pandoc.text.lower(s)
end

local function inizia(s, prefisso)
  return s:sub(1, #prefisso) == prefisso
end

local function tipo(s)
  if not s then return nil end
  if inizia(s, "regesto") or inizia(s, "trascrizione") then return "regesto" end
  if inizia(s, "nota a margine") or s == "margine" then return "margine" end
  if s == "caption" or inizia(s, "didascalia") or s == "image caption"
     or s == "table caption" then return "didascalia" end
  if inizia(s, "citazione") or s == "quote" or s == "intense quote"
     or s == "block text" then return "citazione" end
  return "altro"
end

-- Stili di carattere, segnalibri e ancore di Word: resta solo il testo.
function Span(el)
  if el.classes:includes("anchor") then
    if #el.content == 0 then return {} end
    return el.content
  end
  if el.attributes["custom-style"] then
    return el.content
  end
  return nil
end

-- Stili di paragrafo non riconosciuti, ovunque si trovino (note, elenchi,
-- tabelle): resta solo il testo.
function Div(el)
  if tipo(stile(el)) == "altro" then
    return el.content
  end
  return nil
end

-- Immagini: via le dimensioni di Word; il "testo alternativo" resta come
-- descrizione per chi non vede (fig-alt), non come didascalia.
function Image(el)
  local alt = pandoc.utils.stringify(el.caption)
  el.attributes["width"] = nil
  el.attributes["height"] = nil
  el.caption = {}
  local basso = pandoc.text.lower(alt)
  if alt ~= "" and not basso:find("generat") and not basso:find("automatic") then
    el.attributes["fig-alt"] = alt
  end
  return el
end

local function solo_immagine(blocco)
  if blocco.t ~= "Para" and blocco.t ~= "Plain" then return nil end
  local trovata = nil
  for _, x in ipairs(blocco.content) do
    if x.t == "Image" then
      if trovata then return nil end
      trovata = x
    elseif x.t ~= "Space" and x.t ~= "SoftBreak" and x.t ~= "LineBreak" then
      return nil
    end
  end
  return trovata
end

local function inline_di(blocchi)
  local uscita = pandoc.List()
  for _, b in ipairs(blocchi) do
    if b.content and (b.t == "Para" or b.t == "Plain") then
      if #uscita > 0 then uscita:insert(pandoc.Space()) end
      uscita:extend(b.content)
    end
  end
  return uscita
end

local function riquadro_regesto(blocchi)
  local contenuto = pandoc.List()
  local titolo = pandoc.List({ pandoc.Str("Regesto e trascrizione") })
  local inizio = 1
  if blocchi[1] and (blocchi[1].t == "Para" or blocchi[1].t == "Plain") then
    titolo = blocchi[1].content
    inizio = 2
  end
  -- livello 1: Pandoc lo abbassa a 2 insieme a tutti gli altri titoli
  contenuto:insert(pandoc.Header(1, titolo))
  for i = inizio, #blocchi do contenuto:insert(blocchi[i]) end
  return pandoc.Div(contenuto, pandoc.Attr("", { "callout-note", "trascrizione" },
    { { "collapse", "true" }, { "appearance", "simple" } }))
end

local function sistema(blocchi)
  local uscita = pandoc.List()
  local i = 1
  while i <= #blocchi do
    local b = blocchi[i]
    local t = (b.t == "Div") and tipo(stile(b)) or nil

    if t == "regesto" or t == "margine" then
      -- unisce i paragrafi consecutivi con lo stesso stile
      local insieme = pandoc.List()
      while i <= #blocchi and blocchi[i].t == "Div" and tipo(stile(blocchi[i])) == t do
        insieme:extend(blocchi[i].content)
        i = i + 1
      end
      if t == "regesto" then
        uscita:insert(riquadro_regesto(insieme))
      else
        uscita:insert(pandoc.Div(insieme, pandoc.Attr("", { "column-margin" })))
      end

    elseif t == "citazione" then
      if #b.content == 1 and b.content[1].t == "BlockQuote" then
        uscita:insert(b.content[1])       -- Pandoc l'aveva già riconosciuta
      else
        uscita:insert(pandoc.BlockQuote(b.content))
      end
      i = i + 1

    elseif t == "didascalia" then
      -- didascalia: la attacco all'immagine che la precede
      local precedente = uscita[#uscita]
      local img = precedente and solo_immagine(precedente)
      if img then
        img.caption = inline_di(b.content)
      else
        uscita:extend(b.content)
      end
      i = i + 1

    elseif t == "altro" then
      uscita:extend(sistema(b.content))
      i = i + 1

    else
      uscita:insert(b)
      i = i + 1
    end
  end
  return uscita
end

function Pandoc(doc)
  doc.blocks = sistema(doc.blocks)
  -- toglie i paragrafi rimasti vuoti
  local puliti = pandoc.List()
  for _, b in ipairs(doc.blocks) do
    if not ((b.t == "Para" or b.t == "Plain") and #b.content == 0) then
      puliti:insert(b)
    end
  end
  doc.blocks = puliti
  return doc
end
