import json
import math
import argparse
import pandas as pd


# Mapeamento: chave do JSON -> nome da coluna no Excel
COLUMN_MAP = {
    "sku_id": "SKU - ID",
    "sku_codigo_wakeme_oferta_parcial": "SKU - Código WakeMe Oferta (Parcial)",
    "sku_intake": "SKU - Intake",
    "bloco": "SKU - Bloco",

    "curso_nivel_ensino_id": "Curso - NivelEnsino - ID",
    "curso_nivel_ensino_nome": "Curso - NivelEnsino - Nome",

    "habilitacao_codigo_erp": "Habilitação - Código ERP",
    "habilitacao_nome": "Habilitação - Nome",

    "modalidade_id": "Modalidade - ID",
    "modalidade_nome": "Modalidade - Nome",

    "curso_id_erp": "Curso - ID ERP",
    "curso_id_site": "Curso - ID Site",
    "curso_nome_comercial": "Curso - Nome Comercial",
    "curso_nome_academico": "Curso - Nome Acadêmico",
    "curso_nome_hubspot": "Curso - Nome HubSpot",

    "sku_uf": "SKU - UF",
    "sku_cidade": "SKU - Cidade",

    "unidade_id_erp": "Unidade - ID ERP",
    "unidade_nome": "Unidade - Nome",

    "sku_turno_id_erp": "SKU - Turno ID ERP",
    "sku_turno_id_mid": "SKU - Turno ID Mid",
    "sku_turno_sigla": "SKU - Turno Sigla",
    "sku_turno_nome": "SKU - Turno Nome",

    "curso_duracao": "Curso - Duração",
}


def normalize_value(v):
    """Converte NaN/NaT em None e floats inteiros em int."""
    if v is None:
        return None
    # pandas usa NaN (float) pra vazio
    if isinstance(v, float) and math.isnan(v):
        return None
    # Timestamp / datetime
    if hasattr(v, "to_pydatetime"):
        return v.to_pydatetime().isoformat()
    # Se veio 10.0, vira 10
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v


def xlsx_to_json_rows(xlsx_path: str, sheet_name=None):
    df = pd.read_excel(xlsx_path, sheet_name=sheet_name)

    # Valida colunas obrigatórias
    missing_cols = [col for col in COLUMN_MAP.values() if col not in df.columns]
    if missing_cols:
        raise ValueError(
            "Colunas não encontradas no XLSX:\n- " + "\n- ".join(missing_cols)
        )

    rows = []
    for _, row in df.iterrows():
        obj = {}
        for out_key, excel_col in COLUMN_MAP.items():
            obj[out_key] = normalize_value(row.get(excel_col))
        rows.append(obj)

    return rows


def main():
    parser = argparse.ArgumentParser(description="Converte XLSX em JSON por linha.")
    parser.add_argument("input", help="Caminho do arquivo .xlsx")
    parser.add_argument(
        "-o", "--output",
        default="output.json",
        help="Arquivo de saída .json (default: output.json)"
    )
    parser.add_argument(
        "--sheet",
        default=0,
        help="Nome da aba (sheet). Se omitido, usa a primeira."
    )
    args = parser.parse_args()

    data = xlsx_to_json_rows(args.input, sheet_name=args.sheet)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"OK: gerado {args.output} com {len(data)} itens.")


if __name__ == "__main__":
    main()