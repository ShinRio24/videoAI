from fugashi import Tagger

tagger = Tagger()  # uses unidic-lite by default
print(tagger.parse("これはテストです。"))
