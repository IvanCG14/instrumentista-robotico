#!/usr/bin/env python3
"""Entrena el clasificador de intención SetFit y lo guarda con su labels.json.

Uso:
    python3 tools/train_intent_setfit.py --out ~/models/intent_setfit
    # opcional: --data mi_dataset.json  (lista de {"text": "...", "label": "give_instrument"})

IMPORTANTE: all-MiniLM-L6-v2 se entrenó con texto en inglés. Para comandos en español usa un
modelo multilingüe (por defecto aquí: paraphrase-multilingual-MiniLM-L12-v2, también en
sentence-transformers y de tamaño similar).

Requiere: pip install "setfit>=1.0" datasets
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from surgical_assistant.nlu import INTENTS, normalize  # noqa: E402

# Dataset semilla (amplíalo con frases reales de tu quirófano simulado: 8-16 por clase basta para SetFit).
SEED = {
    'give_instrument': [
        'pasame el bisturi', 'dame la pinza', 'alcanzame las tijeras', 'necesito el porta agujas',
        'entregame la pinza hemostatica', 'traeme el bisturi', 'quiero las tijeras',
        'pasame la pinza de diseccion', 'dame el hemostato', 'ocupo el bisturi por favor',
        'pasame las tijeras de mayo', 'necesito la pinza', 'alcanzame el porta agujas',
        'dame el mosquito', 'pasame el escalpelo ahora',
    ],
    'return_instrument': [
        'toma el bisturi', 'recibe la pinza', 'guarda las tijeras', 'recoge el porta agujas',
        'devuelve el bisturi a la mesa', 'llevate la pinza', 'retira las tijeras',
        'toma el hemostato', 'recibe el porta agujas por favor', 'guarda el bisturi',
        'recoge la pinza de diseccion', 'toma las tijeras',
    ],
    'stop': [
        'alto', 'detente', 'stop', 'para', 'emergencia', 'cancela', 'basta',
        'detente ahora', 'alto alto', 'cancela eso', 'para ya', 'stop robot',
    ],
    'home': [
        'posicion inicial', 'vuelve a casa', 'regresa a inicio', 've a home', 'descansa',
        'vuelve a la posicion inicial', 'regresa a casa', 've a posicion de inicio',
        'home', 'vuelve a inicio por favor', 've a casa',
    ],
    'unknown': [
        'que hora es', 'buenos dias', 'la paciente esta estable', 'sube la luz del quirofano',
        'pasa el gasometro', 'necesito mas succion', 'estamos listos para cerrar',
        'puede abrir la puerta', 'como esta la presion', 'gracias', 'ok', 'la sutura esta lista',
    ],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, help='Directorio de salida del modelo')
    ap.add_argument('--base', default='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    ap.add_argument('--data', default='', help='JSON opcional: [{"text":..., "label":...}, ...]')
    ap.add_argument('--epochs', type=int, default=1)
    ap.add_argument('--iterations', type=int, default=20, help='Pares contrastivos por muestra')
    ap.add_argument('--batch', type=int, default=16)
    args = ap.parse_args()

    from datasets import Dataset
    from setfit import SetFitModel, Trainer, TrainingArguments

    if args.data:
        with open(args.data, 'r', encoding='utf-8') as f:
            rows = json.load(f)
    else:
        rows = [{'text': t, 'label': lab} for lab, texts in SEED.items() for t in texts]

    labels = list(INTENTS)
    texts = [normalize(r['text']) for r in rows]
    y = [labels.index(r['label']) for r in rows]
    ds = Dataset.from_dict({'text': texts, 'label': y}).shuffle(seed=42)
    split = ds.train_test_split(test_size=0.2, seed=42)

    model = SetFitModel.from_pretrained(args.base)
    targs = TrainingArguments(batch_size=args.batch, num_epochs=args.epochs,
                              num_iterations=args.iterations)
    trainer = Trainer(model=model, args=targs, train_dataset=split['train'],
                      eval_dataset=split['test'])
    trainer.train()
    print('Evaluación (split 20%):', trainer.evaluate())

    os.makedirs(args.out, exist_ok=True)
    model.save_pretrained(args.out)
    with open(os.path.join(args.out, 'labels.json'), 'w', encoding='utf-8') as f:
        json.dump(labels, f)
    print('Modelo guardado en', args.out)


if __name__ == '__main__':
    main()
