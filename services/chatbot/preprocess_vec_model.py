import fasttext.util
import fasttext

#download fasttext model and reduce model size
fasttext.util.download_model('zh', if_exists='ignore')
og_model = fasttext.load_model('cc.zh.300.bin')
fasttext.util.reduce_model(og_model, 100)
og_model.save_model('cc.zh.100.bin')

from gensim.models import fasttext as ft
#extract wordvectors from reduced model and save them to be copied to image
reduced_model = ft.load_facebook_model("cc.zh.100.bin")
word_vectors = reduced_model.wv
word_vectors.save("cc.zh.100.vec")