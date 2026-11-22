# Słownik roboczy polskiego przekładu

Próbka obejmuje początek wprowadzenia, od opisu kursu po trzy przykłady z prac nad Pine. Podstawą przekładu jest [tekst chiński, wiersze 1–15](https://github.com/bojieli/ai-agent-book/blob/4d0077a59a6046fe79b53c3cbba6e877372b3d6a/book/introduction.md#L1-L15). Przy rozstrzyganiu wątpliwości pierwszeństwo ma wydanie chińskie; do wydania angielskiego można sięgnąć pomocniczo.

Pomysł pilotażu i zakres słownika zaproponował Krzysztof Skomra w [zgłoszeniu nr 1088](https://github.com/bojieli/ai-agent-book/issues/1088). Ten roboczy przekład powstał z użyciem AI. Czeka na recenzję techniczną i językową, w tym ocenę proponowanych terminów przez polskojęzycznych czytelników. Pierwsza osoba we wprowadzeniu odnosi się do autora książki.

| Termin użyty w wydaniu chińskim | Termin angielski | Propozycja polska | Przykład lub uwaga |
| --- | --- | --- | --- |
| Harness | agent harness | warstwa wykonawcza agenta (*harness*) | Obejmuje m.in. przygotowanie kontekstu, obsługę narzędzi, egzekwowanie ograniczeń i sprawdzanie wyników. Gdy mowa o historii samej nazwy, zachowujemy angielskie *agent harness*. |
| 上下文工程 | context engineering | inżynieria kontekstu | Obejmuje dobór, porządkowanie i aktualizację informacji, które model otrzymuje przy podejmowaniu kolejnej decyzji. |
| 工具调用 | tool calling | wywoływanie narzędzi | Pojedyncze zdarzenie to „wywołanie narzędzia”. W opisie działania systemu warto rozróżnić żądanie modelu, wykonanie operacji i zwrócony wynik. |
| 轨迹 | trajectory | trajektoria | Przy pierwszym użyciu można objaśnić termin jako zapis kolejnych obserwacji i działań. W uczeniu przez wzmacnianie zapis obejmuje też nagrody. |
| Agent 评估 | agent evaluation | ocena działania agenta | Gdy mowa o procedurze: „ocenić działanie agenta na zbiorze zadań”. Przy porównywaniu wyników warto nazwać mierzoną wielkość, np. odsetek ukończonych zadań. |
| 多 Agent 系统 | multi-agent systems | systemy wieloagentowe | „Współpraca agentów” opisuje sposób pracy poszczególnych agentów w takim systemie. |
