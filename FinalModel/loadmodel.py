import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import pickle
from flask import jsonify
import json
import logging

dictionary = {
  ' ': '',
  '': '',
  "RT": "Root", 
  "N": "Noun",
  "V": "Verb",
  "AV": "Adverb",
  "AJ": "Adjective",
  "PS": "Postposition",
  "PN": "Pronoun",
  "NM": "Numeral",
  "C": "Conjunction",
  "I": "Interjection",
  "D": "Determinant",
  "PR": "Proper Noun",
  "P": "Particle",
  "VP": "Verb Particle",
  "NOM": "Nominative",
  "GEN":  "Genitive",
  "DAT":  "Dative",
  "ACC":  "Accusative",
  "ABL":  "Ablative",
  "AGN":  "Agentive",
  "INT":  "Instrumental",
  "LOC":  "Locative",
  "VOC":  "Vocative",
  "1":  "First Person",
  "2":  "Second Person",
  "3":  "Third Person",
  "SG":  "Singular",
  "PL":  "Plural",
  "MS":  "Masculine",
  "FE":  "Feminine",
  "NE":  "Neuter",
  "NT":  "Non Past",
  "NP":  "Present Participle",
  "GE":  "Gerund",
  "PT":  "Past Tense",
  "IM":  "Imperfect",
  "PP":  "Past Participle",
  "IN":  "Indicative",
  "IP":  "Imperative",
  "CN":  "Conditional",
  "IF":  "Infinitive",
  "DR":  "Derived",
  "PG":  "Progressive",
  "PO":  "Positive",
  "NG":  "Negative",
  "PM":  "Permissive",
  "OP":  "Optative",
  "EV":  "Eventive",
  "PV":  "Pure Verb",
  "DF":  "Definite",
  "ID":  "Indefinite",
  "CJ":  "conjunction",
  "FN":  "Final",
  "UN":  "Uncountable",
}

loaded_models = load_model("network.h5")

f = open('word2ind.pckl', 'rb')
word2ind = pickle.load(f)
f.close()

f = open('ind2label.pckl', 'rb')
ind2label = pickle.load(f)
f.close()

f = open('maxlen.pckl', 'rb')
maxlen = pickle.load(f)
f.close()

print(len(word2ind), len(ind2label), maxlen)

# function to morphological analysis
def morphological_analyzer(word):
  splittedWord = [list(i) for i in word]
  encodedWord = [[word2ind[j] for j in c] for c in splittedWord]
  paddedWord = pad_sequences(encodedWord, maxlen=maxlen)
  y_predicted = loaded_models.predict(paddedWord)

  results = []
  temp = []
  for i in range(len(y_predicted)):
    x = np.argmax(y_predicted[i], axis=1)
    for j in x:
      if j != 0:
        temp.append(ind2label[j])
    
    results.append(temp)
    temp = []

  return results[0]
  # for i,val in enumerate(results):
  #     print(word[i], val,'\n')

# word = ['නායකයාගෙන්', 'කුසලානවලට', 'නිමල්ගෙන්', 'ජපානයට', 'කඩුල්ලක්', 'පිළිතුරුවල', 'හෙළයෝ', 'අංකනය']
# print(morphological_analyzer(word))

# word = ['අංකන', 'අංකනත්', 'අංකනය', 'අංකනයක', 'අංකනයකට', 'අංකනයකටත්', 'අංකනයකටයි', 'අංකනයකත්', 'අංකනයකයි', 
#          'අංකනයකි', 'අංකනයකිනි', 'අංකනයකිනුත්', 'අංකනයකින්', 'අංකනයකුත්', 'අංකනයක්', 'අංකනයට', 'අංකනයටත්', 'අංකනයටයි', 
#          'අංකනයත්', 'අංකනයයි', 'අංකනයි', 'අංකනයෙ', 'අංකනයෙත්', 'අංකනයෙනි', 'අංකනයෙනුත්', 'අංකනයෙන්', 'අංකනයෙයි', 
#          'අංකනයෙහි', 'අංකනයෙහිත්', 'අංකනයෙහියි', 'අංකනයේ', 'අංකනයේත්', 'අංකනයේයි', 'අංකනවල', 'අංකනවලට', 
#          'අංකනවලටත්', 'අංකනවලටයි', 'අංකනවලත්', 'අංකනවලයි', 'අංකනවලිනි', 'අංකනවලිනුත්', 'අංකනවලින්']
# print(morphological_analyzer(word))

from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)


@app.route('/')
def page():
  return render_template('page.html')

@app.route('/', methods=['GET', 'POST'])
def morphological_analysis():
  if request.method == "POST":
    word = request.form['word']
    # morphological analysis
    input = []
    input.append(word)
    results = morphological_analyzer(input)
    morph_temp = list(results[0])
    without_tilda = [ x for x in morph_temp if "~" not in x ]
    
    # morphemes
    morph = []
    for i in without_tilda:
          if ':' in i:
             morph.append(i.split(':')[0])

    noRoot = ''.join(morph)

    if(noRoot != "" and (noRoot in word)):   
      morph.insert(0, word.split(''.join(morph))[0])
    else:
    # elif(noRoot == ""):
      morph.insert(0, word)

    tempValue = morphological_analyzer(input)
    for i in range(len(tempValue)):
      toList = list(tempValue[i])
      toList[0] = morph[0] + ":" + toList[0]
      for j in range(len(toList)):
            temp = toList[j].split(':')[1].split('+')
            for q in range(len(temp)):
                  if(temp[q] in dictionary):
                    temp[q] = dictionary[temp[q]]    
                  # print(temp[q])
            description = '+'.join(temp)
            toList[j] = toList[j].split(":")[0] + ":" + description      

      tempValue[i] = tuple(toList)

    # output = json.dumps(tempValue, ensure_ascii=False)
    output = tempValue
    # print('\n',tempValue,'\n')
    # final_morph = json.dumps(morph, ensure_ascii=False)
    final_morph = morph
    # word = json.dumps(word, ensure_ascii=False)
    return render_template('page.html', word = word, morph = final_morph, result =  output)
    # return redirect(url_for('Results', word = word, morph = final_morph, result = output))

# @app.route('/<word>/<morph>/<result>')
# def Results(word, morph, result):
#       return render_template('page.html', word = word, morph = morph, result =  result)
  
if __name__ == "__main__":
  app.run(use_reloader = True, debug = False)