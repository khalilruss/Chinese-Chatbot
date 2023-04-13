num='[一二三四五六七八九]'
fullNum='[一二三四五六七八九十]'
yearNum='[一二三四五六七八九零]'
liangNum='[一两二三四五六七八九]'
adj='(?:[\p{Han}]+(?:VA|JJ))'
adverb='(?:[\p{Han}]+AD)'
verb='(?:[\p{Han}]+(?:VV|VE|VC)(?:了(?:AS|SP))?)'
number='(?:[\p{Han}\d]+CD)'
timeNum='[一两三四五六七八九十]'
name='(?:[\p{Han}]+|[a-zA-Z]+)(?:NN|NR)'
punct='(?:[\p{Punct}]PU)'
preposition='(?:[\p{Han}]+(?:[P]|CC))'
measureWord='(?:[\p{Han}][M])'
timeNoun='(?:[\p{Han}]+NT)'
year=fr'(?:(?:\d{{4}}|{yearNum}{{4}})年NT)'
obj=fr'(?:(?:(?:[\p{{Han}}]+JJ)|{number}?{measureWord}?)?[\p{{Han}}]+(?:NN|NR|PN)|[a-zA-Z]+(?:NN|NR))'
subj=fr'(?:{timeNoun}?[\p{{Han}}]+DT{measureWord}?{obj}{timeNoun}?|{timeNoun}?{obj}+{timeNoun}?(?:(?:的(?:DE[GC]|SP))?{obj}|[\p{{Han}}]+(?:[P]|CC){obj}+|(?:{number}?{measureWord}))?{timeNoun}?|{timeNoun}(?:的(?:DE[GC]|SP))?)'
place=fr'(?:这里PN|这儿PN|那儿PN|那里PN|哪儿PN|哪里PN|哪儿PN|(?:[\p{{Han}}]+DT{measureWord}|{obj}(?:的(?:DE[GC]|SP))?)?(?:[\p{{Han}}]+(?:NN|NR))+(?:[\p{{Han}}]+LC)?)'
month=fr'(?:[1-9]|1[0-2]|{num}|十[一二]?)月NT'
day=fr'(?:[1-9]|[12]\d|3[01]|{num}|(?:十|二十){num}?|三十[一]?)(?:日NT|号NT)'
verbPhrase=fr'{adverb}*{verb}+{preposition}?{subj}?'
command=fr'(?:{verb}(?:{adverb}|{subj})?)'

grammarRules=[{'word':'没[有]?','rules': [{'rule':'没有/没 (+ Obj.)', 'pattern':fr'没[有]?(?:VE|AD){obj}', 'level':1},
                            {'rule':'Subj. + 没有/ 没 + Verb', 'pattern':fr'{subj}{adverb}*没[有]?(?:VE|AD){verb}+', 'level':1},
                            {'rule':'没有 / 没 with 了 is incorrect', 'pattern':r'[\p{Han}\w]+没[有]?(?:VE|AD)[\p{Han}\w]+了(?:AS|SP)', 'level':1}]},
        {'word':'[^没]有','rules': [{'rule':'不 + 有 is incorrect', 'pattern':r'不AD有VE', 'level':1},
                            {'rule':'Place + 有 + Obj.', 'pattern':fr'{place}{adverb}*有VE{obj}', 'level':1},
                            {'rule':'Subj. + 有 + Obj. ', 'pattern':fr'{subj}{adverb}*有VE{obj}', 'level':1},
                            {'rule':'Subj. + 有 没有 + Obj. ', 'pattern':fr'{subj}有没有(?:VV|AD)(?:{verb}[\p{{Han}}]+AS)?{obj}', 'level':1}]},
        {'word':'不','rules': [{'rule':'Subj. + 不 + Verb + Obj.', 'pattern':fr'{subj}不AD{verb}+{obj}', 'level':1},
                            {'rule':'Subj. + 不 + Adj.', 'pattern':fr'{subj}{adverb}?不AD{adj}', 'level':1},
                            {'rule':'Subj. + Verb + 不 + Verb (+ Obj.) ', 'pattern':fr'{subj}?{verb}不AD{verb}{obj}?', 'level':1},
                            {'rule':'Subj. + Adj + 不 + Adj (+ Obj.) ', 'pattern':fr'{subj}?{adj}不AD{adj}{obj}?', 'level':1},
                            ]},
        {'word':'都','rules': [{'rule':'Subj. + 都(all) + [Verb Phrase]', 'pattern':fr'(?={preposition}{obj}?){obj}都AD{verbPhrase}', 'level':1},
                            {'rule':'Subj. + 都(both) + [Verb Phrase]', 'pattern':fr'{obj}(?:{number}{measureWord}|[\p{{Han}}]+(?:P|CC){obj}+)都AD{verbPhrase}', 'level':1}]},
        {'word':'也','rules': [{'rule':'Subj. + 也 + Verb / [Verb Phrase]', 'pattern':fr'{subj}也AD{verbPhrase}', 'level':1},
                            {'rule':'Subj. + 也 (+ Adv.) + Adj', 'pattern':fr'{subj}也AD{adverb}*{adj}', 'level':1}]},                    
        {'word':'和','rules': 'Noun 1 + 和 + Noun 2', 'pattern':fr'{subj}和(?:P[^A-Z]|CC){subj}', 'level':1},
        {'word':'岁','rules': 'Subj. + Number + 岁 (+ 半)', 'pattern':fr'{subj}{adverb}*{number}岁M(?:半CD)?', 'level':1},
        {'word':'个','rules': [{'rule':'Number + 个 + Noun', 'pattern':fr'{number}个M{obj}', 'level':1},
                            {'rule':'Verb + 个 + Noun', 'pattern':fr'{verb}个M{obj}', 'level':1}]},
        {'word':fr'(?:(?:\d+年\d+月\d+(?:日|号)|\d+月\d+(?:日|号)|\d+年\d+月)|(?:{yearNum}+年{fullNum}+月{fullNum}+(?:日|号)|{fullNum}+月{fullNum}+(?:日|号)|{yearNum}+年{fullNum}+月))','rules': 'Number 年 + Number 月 + Number 日/号', 'pattern':fr'(?:{year}{month}{day}|{month}{day}|{year}{month})', 'level':1},
        {'word':'十','rules':'Number + 十 (+ Number) ', 'pattern':fr'{num}?十{num}?CD', 'level':1},
        {'word':'百','rules':'Number + 百 (+ 零 + Number/+ Number + 十 + Number )', 'pattern':fr'{liangNum}百(?:零{num}|{num}十{num}?)?CD', 'level':1},
        {'word':'千','rules':'Number + 千 (+ 零 + Number/+ Number + 十 + Number )', 'pattern':fr'{liangNum}千(?:零(?:{num}|{num}十{num}?)|{liangNum}百(?:零{num}|{num}十{num}?)?)?CD', 'level':1},

        {'word':'星期','rules': '星期 + Number', 'pattern':r'星期[一二三四五六天日]NT', 'level':1},
        {'word':'点','rules': '(Date and/or time of day +) x 点 (+ 半)', 'pattern':fr'(?:[\p{{Han}}]+NT)*(?:{timeNum}|十[一二]?)点[半]?(?:NT|CD)', 'level':1},
        {'word':'的','rules':[{'rule':'Noun1 + 的 + Noun2', 'pattern':fr'{obj}的(?:DE[GC]|SP){obj}', 'level':1},
                            {'rule':'Adj. + 的 + Noun ', 'pattern':fr'{adj}的(?:DE[GC]|SP){obj}', 'level':1},
                            {'rule':'Adj. + 的 ', 'pattern':fr'{adj}的(?:DE[GC]|SP)(?!{obj})', 'level':1},
                            {'rule':'Phrase + 的 + Noun  ', 'pattern':fr'(?:{subj}{adverb}*{verb}|{adverb}*{verb}{subj})的(?:DE[GC]|SP){obj}', 'level':1},
                            {'rule':'Phrase + 的 ', 'pattern':fr'(?:{subj}{adverb}*{verb}|{adverb}*{verb}{subj})的(?:DE[GC]|SP)(?!{obj})', 'level':1},]}, 
        {'word':'呢','rules': [{'rule':'Topic + 呢 ？', 'pattern':fr'(?:{obj}|{timeNoun})+呢SP？', 'level':1},
                            {'rule':'[Missing Person / Thing] + 呢 ？', 'pattern':r'[\p{Han}\w]+(?:NN|NR|NN|PN)呢SP？', 'level':3}]},
        {'word':'[^酒]吧','rules': 'Command + 吧 ', 'pattern':fr'{command}吧SP', 'level':1},
        {'word':'[^现]在','rules': [{'rule':'Subj. + 在 + Place', 'pattern':fr'{subj}+{adverb}*在(?:VV|P[^A-Z]|AD){place}', 'level':1},
                            {'rule':'Subj. + (正)在 + Verb + Obj. ', 'pattern':fr'{subj}+{adverb}*[正]?在(?:VV|[P]|AD)(?:{preposition}{obj})?{verb}+{obj}?', 'level':2}]},
        {'word':'叫','rules': 'Subj. + 叫 + [Name]', 'pattern':fr'{subj}叫VV(?:{name}|什么PN)', 'level':1},
        {'word':'去','rules': [{'rule':'Subj. + 去 + [Place]', 'pattern':fr'{subj}{verb}?{adverb}*去VV{place}', 'level':1},
                            {'rule':'Subj. + 去 + Verb', 'pattern':fr'{subj}{verb}?去VV{verb}', 'level':1}]},
        {'word':'姓','rules': 'Subj. + 姓 + [Surname]  ', 'pattern':fr'{subj}{adverb}*姓VV(?:{name}|什么PN)', 'level':1},
        {'word':'能','rules': 'Subj. + 能 + Verb (+ Obj.)', 'pattern':fr'{subj}{adverb}*能VV{adverb}*{verb}{obj}?', 'level':1},
        {'word':'会','rules': 'Subj. + 会 + Verb (+ Obj.)  ', 'pattern':fr'{subj}{adverb}*会VV{verb}{obj}?', 'level':1},
        {'word':'可以','rules': 'Subj. + 可以 + Verb (+ Obj.)  ', 'pattern':fr'{subj}{adverb}*可以VV(?:[\p{{Han}}]P{place})?{verb}{obj}?', 'level':1},
        {'word':'要','rules': 'Subj. + 要 + Verb (+ Obj.)  ', 'pattern':fr'{subj}要VV{verb}{obj}?', 'level':1},
        {'word':'怎么','rules': [{'rule':'Subj. + 怎么 + Verb (+ Obj.)', 'pattern':fr'{subj}(?:{adverb}*{verb})?怎么AD(?:{preposition}{obj})?{verb}{obj}?？PU', 'level':1},
                                {'rule':'Topic + 怎么 + Verb', 'pattern':fr'{obj}怎么AD{verb}？PU', 'level':1},]},
        {'word':'不要','rules': '不要 + Verb ', 'pattern':fr'不AD要VV(?:{adverb}*{adj})?{verb}', 'level':1},
        {'word':'还是','rules':[ {'rule':'Option A + 还是 + Option B ? ','pattern':fr'(?<!{subj}{adverb}*{verb}+)(?:{subj}|{adverb}?{adj}(?:的(?:DE[GC]|SP))|{number}{measureWord})还是(?:AD|CC)(?:{subj}|{adverb}?{adj}(?:的(?:DE[GC]|SP))|{number}{measureWord})', 'level':1},
                            {'rule':'Subj. + Verb + Option A + 还是 + Option B ?','pattern':fr'{subj}{adverb}*{verb}+{subj}还是(?:AD|CC){subj}', 'level':1}]},
        {'word':'[\p{Han}]+','rules':[{'rule': 'Subj. + Verb (+ Obj.) ','pattern':fr'{subj}{adverb}*{verb}+{subj}?', 'level':1}]},
        {'word':'是','rules':[{'rule':'Noun 1 + 是 + Noun 2 ','pattern':fr'{subj}{adverb}*是VC{subj}', 'level':1},
                            {'rule':'Noun + 是 + Adj is incorrect ','pattern':fr'{subj}{adverb}*是VC{adj}', 'level':1},
        ]},
        {'word':'太','rules':'太 + Adj. + 了','pattern':fr'太AD{adj}了(?:AS|SP)', 'level':1},
        {'word':'很','rules':'Noun + 很 + Adj.','pattern':fr'{subj}{adverb}*很AD{adj}', 'level':1},
        {'word':'什么','rules':[{'rule':'Subj. + Verb + 什么 + (Noun)?','pattern':fr'{subj}{adverb}*{verb}+什么(?:PN|DT){obj}?', 'level':1},
                            {'rule':'Subj. + 什么时候 + Predicate?','pattern':fr'{subj}什么DT时候NN{verb}', 'level':1},
                            {'rule':'Subj. + 为什么 + Predicate?','pattern':fr'{subj}为什么AD{adverb}*{verb}', 'level':1}]},
        {'word':'(?:哪里|哪儿)','rules':'Subj. + Verb + 哪里/哪儿?','pattern':fr'{subj}{adverb}*{verb}+哪(?:里|儿)PN', 'level':1},
        {'word':'哪个','rules':'Subj. + Verb + 哪个 (+ Noun)?','pattern':fr'{subj}{adverb}*{verb}?{preposition}?哪(?:DT个M|个PN){obj}?', 'level':1},
        {'word':'谁','rules':[{'rule':'Subj. + 是 + 谁?','pattern':fr'{subj}{adverb}*{verb}谁PN', 'level':1},
                            {'rule':'谁 + Verb?','pattern':fr'谁PN{verb}+', 'level':1}]},
        {'word':'吗','rules':[{'rule':'⋯⋯， 好/对/是/可以 + 吗？','pattern':'[\p{Han}\w]+，PU(?:对VA|是VC|好VA|可以VV)吗SP？PU', 'level':1},
                            {'rule':'[Statement] + 吗？','pattern':fr'(?<!(?:，PU|，PU[\p{{Han}}]))(?:{subj}*(?:{adverb}*(?:{verb}|{adj})+{timeNoun}*{subj}*|(?:{number}?{measureWord})))+吗SP？PU', 'level':1}]},
        {'word':'死','rules':'Adj. + 死了','pattern':fr'{adj}?死VV了(?:AS|SP)', 'level':2},
        {'word':'差不多','rules':[{'rule':'Subj. + 差不多','pattern':fr'{subj}+(?:都AD)?差不多VA', 'level':2},
                                {'rule':'A + 跟 / 和 +B + 差不多','pattern':fr'{subj}+(?:和|跟)(?:[P]|CC){subj}+差不多VA', 'level':2},
                                {'rule':'差不多 + Adj. / Verb','pattern':fr'差不多AD(?:{verb}|{adj})', 'level':2},
                                {'rule':'差不多 ＋ [Quantity Phrase] / [Time Phrase]','pattern':fr'差不多AD{number}', 'level':2}]},
        {'word':'一直','rules':'Subj. + 一直 + Predicate ','pattern':fr'{subj}一直AD(?:{preposition}{subj}{verbPhrase}?|{subj}?{verbPhrase})', 'level':2},
        {'word':'已经','rules':[{'rule':'已经 + [Verb Phrase] + 了','pattern':fr'已经AD{verbPhrase}了(?:AS|SP)', 'level':2},
                            {'rule':'已经 + (很 +) Adj. + 了','pattern':fr'已经AD(?:很AD)?{adj}了(?:AS|SP)', 'level':2},
                            {'rule':'已经 + Time + 了 ','pattern':fr'已经AD(?:{number}?{measureWord}){obj}?了(?:AS|SP)', 'level':2},]},
        {'word':'总是','rules':[{'rule':'Subj. + 总是 + Verb','pattern':fr'{subj}(?:总是AD|总AD是VC){obj}?{verb}', 'level':2},
                            {'rule':'总是 + Adv. + Adj. ','pattern':fr'(?:总是AD|总AD是VC){adverb}{adj}', 'level':2},]},
        {'word':'还[^是]','rules':[{'rule':'Subj. + Verb + Obj. 1， 还 + Verb + Obj. 2 ','pattern':fr'{subj}{adverb}*{preposition}?{verb}+(?:{obj}{punct})+还AD{verb}+{obj}', 'level':2},
                                {'rule':'Subj. + 还 + 好 / 可以 / 行 / 不错 ','pattern':fr'{subj}还AD(?:好VA|可以VV|行VA|不错VA)', 'level':2},]},
        {'word':'刚','rules':[{'rule':'Subj. + 刚 + Verb ','pattern':fr'{subj}[刚]{{1,2}}AD{verb}(?!{obj}?{number}{measureWord}{obj}?){obj}?', 'level':2},
                            {'rule':'Subj. + 刚 + Verb (+ Obj.) + Duration ','pattern':fr'{subj}[刚]{{1,2}}AD{verb}{obj}?{number}{measureWord}{obj}?', 'level':2}]},
        {'word':'只','rules':'只 + Verb ','pattern':fr'只AD{verb}+', 'level':2},
        {'word':'就','rules':'..., 就 + Verb Phrase ','pattern':fr'就AD(?:{preposition}{subj})?{verbPhrase}', 'level':2},
        {'word':'别','rules':'别 + Verb (+ Obj.) ','pattern':fr'别AD{verb}{obj}?', 'level':2},
        {'word':'一边','rules':'Subj. + 一边 + Verb (，) + 一边 + Verb ','pattern':fr'{subj}?{adverb}*{verb}?一边AD{adverb}*{verb}{obj}?(?:{punct})?一边AD{adverb}*{verb}{obj}?', 'level':2},
        {'word':'多','rules':[{'rule':'Subj. + 多 + Adj. ?','pattern':fr'{subj}多(?:AD|CC|VA){adj}(?:吗SP)?？PU', 'level':2},
                            {'rule':'Subj. + 多 + Adj.','pattern':fr'{subj}{punct}?多(?:AD|CC|VA){adj}(?!吗SP)(?!？PU)', 'level':2},]},
        {'word':'一样','rules':[{'rule':'Noun 1 + 跟 / 和 + Noun 2 + 一样','pattern':fr'{subj}(?:和|跟)(?:[P]|CC){subj}{adverb}*一样(?:VA|AD)(?!{adj})', 'level':2},
                            {'rule':'Noun 1 + 跟 / 和 + Noun 2 + 一样 + Adj.','pattern':fr'{subj}(?:和|跟)(?:[P]|CC){subj}{adverb}*一样(?:VA|AD){adj}', 'level':2}]},
        {'word':'(?:有[一]?点[儿]?)','rules':'Subj. + 有(一)点(儿) + Adj. ','pattern':fr'{subj}有(?:点AD|VE一点CD){adverb}?{adj}', 'level':2},
        {'word':'又','rules':'Subj. + 又 + Adj. 1 + 又 + Adj. 2 ','pattern':fr'{subj}又(?:AD|CC){adj}又(?:AD|CC){adj}', 'level':2},
        {'word':'离','rules':[{'rule':'Place 1 + 离 + Place 2 + Adv. + 近 / 远 ','pattern':fr'{place}离P{place}(?!多AD){adverb}(?:近VA|远VA)(?!吗SP)', 'level':2},
                            {'rule':'Place 1 + 离 + Place 2 (+ Adv.) + 近 / 远 + 吗？ ','pattern':fr'{place}离P{place}{adverb}?(?:近VA|远VA)吗SP', 'level':2},
                            {'rule':'Place 1 + 离 + Place 2 (+ 有) + 多远？  ','pattern':fr'{place}离P{place}(?:有VE)?多AD远VA', 'level':2}]},
        {'word':'更','rules':[{'rule':'更 + Adj.','pattern':fr'(?<!(?:{subj}比P{subj}))更AD{adj}', 'level':2},
                            {'rule':'A 比 B + 更 + Adj.','pattern':fr'{subj}比P{subj}更AD{adj}', 'level':2}]},
        {'word':'不太','rules':[{'rule':'Subj. + 不太 + Adj. ','pattern':fr'{subj}不AD太AD{adj}', 'level':2},
                                {'rule':'Subj. + 不太 + Verb','pattern':fr'{subj}不AD太AD{verb}', 'level':2}]},
        {'word':'真','rules':[{'rule':'真 + Adj.','pattern':fr'真AD{adj}', 'level':2},
                            {'rule':'真 + Verb','pattern':fr'真AD{verb}', 'level':2}]},
        {'word':'最','rules':[{'rule':'最 + Adj. (+ 了)','pattern':fr'最AD{adj}(?:了(?:AS|SP))?', 'level':2},
                            {'rule':'最 + [Psychological Verb] + Obj. (+ 了) ','pattern':fr'最AD{verb}{obj}(?:了(?:AS|SP))?', 'level':2},]}

    ]
