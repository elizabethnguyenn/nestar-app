from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name = "unitary/toxic-bert"
save_dir = "./models/toxic-bert"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

tokenizer.save_pretrained(save_dir)
model.save_pretrained(save_dir)
python download_model.py
