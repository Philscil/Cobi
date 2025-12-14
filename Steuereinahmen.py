import json
import unicodedata
import os
from typing import List, Dict, Any


def _normalize(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip()
    # remove diacritics for more robust matching
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s


def berechne_steuereinnahmen(provinzen_path: str = "Provinzen.json",
                             laender_path: str = "Länder.json",
                             write_output: bool = False,
                             output_path: str = "Laender_steuereinnahmen.json",
                             update_countries: bool = True) -> Dict[str, float]:
    """Lädt Provinzen und Länder und summiert die Steuereinnahmen pro Land.

    Die Zuordnung versucht robust zu sein: zuerst wird geprüft, ob der Provinzname
    mit einem Ländernamen beginnt (z. B. "Deutschland - ..."), dann wird der
    linke Teil vor " - " geprüft, danach wird eine Teilstring-Suche versucht.

    Gibt ein Dict {Land: summe} zurück. Wenn write_output True ist, wird das
    Ergebnis auch nach `output_path` geschrieben.
    """
    if not os.path.exists(provinzen_path):
        raise FileNotFoundError(f"{provinzen_path} nicht gefunden")
    if not os.path.exists(laender_path):
        raise FileNotFoundError(f"{laender_path} nicht gefunden")

    with open(provinzen_path, "r", encoding="utf-8") as f:
        provinces_data = json.load(f)

    with open(laender_path, "r", encoding="utf-8") as f:
        countries_data = json.load(f)

    provinces: List[Dict[str, Any]] = provinces_data.get("Provinzen", [])
    countries_list: List[Dict[str, Any]] = countries_data.get("Länder", [])
    countries: List[str] = [c.get("Name", "") for c in countries_list]

    # prepare normalized country names sorted by length (longer first)
    norm_country_map = {c: _normalize(c).lower() for c in countries}
    countries_sorted = sorted(countries, key=lambda x: -len(x))

    totals: Dict[str, float] = {c: 0.0 for c in countries}
    unknowns: Dict[str, float] = {}

    for prov in provinces:
        name = prov.get("Name", "")
        norm_name = _normalize(name).lower()
        amount = prov.get("Steuereinahmen", 0)
        try:
            amount = float(amount)
        except Exception:
            amount = 0.0

        owner = None

        # strategy 1: startswith country
        for c in countries_sorted:
            nc = norm_country_map.get(c, "")
            if nc and (norm_name.startswith(nc) or norm_name.startswith(nc + " ") or norm_name.startswith(nc + " -")):
                owner = c
                break

        # strategy 2: left part before ' - '
        if owner is None and " - " in name:
            left = _normalize(name.split(" - ")[0]).lower()
            for c in countries_sorted:
                nc = norm_country_map.get(c, "")
                if nc and nc in left:
                    owner = c
                    break

        # strategy 3: substring match
        if owner is None:
            for c in countries_sorted:
                nc = norm_country_map.get(c, "")
                if nc and nc in norm_name:
                    owner = c
                    break

        if owner:
            totals[owner] = totals.get(owner, 0.0) + amount
        else:
            unknowns[name] = unknowns.get(name, 0.0) + amount

    result = {"Länder": []}
    for c in countries:
        result["Länder"].append({"Name": c, "Steuereinnahmen": totals.get(c, 0.0)})

    if unknowns:
        result["Unbekannt"] = unknowns

    # falls gewünscht: Länder.json um die Steuereinnahmen (zum vorhandenen Geld) aktualisieren
    if update_countries:
        # Backup der Originaldatei
        backup_path = laender_path + ".bak"
        with open(laender_path, "r", encoding="utf-8") as lf:
            original_countries = json.load(lf)
        with open(backup_path, "w", encoding="utf-8") as bf:
            json.dump(original_countries, bf, ensure_ascii=False, indent=4)

        # Suche nach einem existierenden Geld-Feld pro Land (mehrere mögliche Feldnamen)
        money_keys = ["Geld", "Guthaben", "Vermoegen", "Vermögen", "Budget", "Kasse", "Money", "Balance"]

        # Aktualisiere die Einträge im geladenen original_countries-Objekt
        for entry in original_countries.get("Länder", []):
            name = entry.get("Name")
            if name is None:
                continue
            tax = totals.get(name, 0.0)
            # find existing numeric money key
            found_key = None
            for k in money_keys:
                if k in entry:
                    try:
                        _ = float(entry[k])
                        found_key = k
                        break
                    except Exception:
                        continue
            if found_key:
                entry[found_key] = float(entry.get(found_key, 0.0)) + float(tax)
            else:
                # set a new field `Geld`
                entry["Geld"] = float(tax)

        # schreibe die aktualisierte Länder.json zurück (mit Änderungen)
        with open(laender_path, "w", encoding="utf-8") as lf:
            json.dump(original_countries, lf, ensure_ascii=False, indent=4)

    if write_output:
        with open(output_path, "w", encoding="utf-8") as out:
            json.dump(result, out, ensure_ascii=False, indent=4)

    return result


if __name__ == "__main__":
    # einfache Ausführung: berechne und schreibe Ergebnis
    res = berechne_steuereinnahmen(write_output=True)
    print("Ergebnis geschrieben nach 'Laender_steuereinnahmen.json'\n")
    for entry in res.get("Länder", []):
        print(f"{entry['Name']}: {entry['Steuereinnahmen']}")
    if res.get("Unbekannt"):
        print("\nNicht zugeordnete Provinzen:")
        for pname, val in res["Unbekannt"].items():
            print(f" - {pname}: {val}")





    