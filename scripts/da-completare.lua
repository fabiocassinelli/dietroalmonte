-- Riquadri "DA COMPLETARE".
--
-- Nel testo si scrivono così:
--
--   ::: {.da-completare}
--   ## DA COMPLETARE — che cosa manca
--   Spiegazione ed esempio di che cosa scrivere.
--   :::
--
-- Nell'anteprima sul computer compaiono come riquadri ben visibili.
-- Quando il sito viene costruito da GitHub Actions (variabile
-- d'ambiente DAM_PUBBLICA=1) vengono tolti: sul sito pubblico e nei
-- PDF non compaiono mai.

local pubblica = os.getenv("DAM_PUBBLICA") == "1"

function Div(el)
  if not el.classes:includes("da-completare") then
    return nil
  end
  if pubblica then
    return {}
  end
  -- Lo trasformo in un riquadro "callout" di Quarto, sempre aperto.
  local classi = { "callout-important", "da-completare" }
  el.classes = pandoc.List(classi)
  el.attributes["appearance"] = "simple"
  el.attributes["icon"] = "false"
  return el
end

-- Nei PDF delle versioni citabili, scripts/rilascio.py chiede di aggiungere
-- in testa una riga con versione, indirizzo e licenza (variabile DAM_TESTATA).
function Pandoc(doc)
  local testata = os.getenv("DAM_TESTATA")
  if testata and testata ~= "" then
    local blocchi = pandoc.read(testata, "markdown").blocks
    for i = #blocchi, 1, -1 do
      table.insert(doc.blocks, 1, blocchi[i])
    end
  end
  return doc
end
