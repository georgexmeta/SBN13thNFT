import json
F,H,N,C,R='Friday the 13th','Halloween','A Nightmare on Elm Street',"Child's Play",'Hellraiser'
Q=[
# Friday the 13th
(F,'Light',"Who is the killer in the original Friday the 13th (1980)?","Pamela Voorhees, Jason's mother",["Jason Voorhees","Crazy Ralph","Alice Hardy"]),
(F,'Light',"What is the name of the summer camp in Friday the 13th?","Camp Crystal Lake",["Camp Silver Lake","Camp Blackwood","Camp Pine Ridge"]),
(F,'Easy',"What does Jason wear over his head in Friday the 13th Part 2 (1981), before the hockey mask?","A burlap sack",["A welding mask","A pillowcase","A gas mask"]),
(F,'Easy',"Who is the last counselor standing at the end of the original Friday the 13th?","Alice",["Ginny","Chris","Tina"]),
(F,'Moderate',"In which film does Jason first put on his hockey mask?","Friday the 13th Part III (1982)",["Friday the 13th Part 2 (1981)","Friday the 13th: The Final Chapter (1984)","Friday the 13th: A New Beginning (1985)"]),
(F,'Moderate',"Who played Mrs. Voorhees in the 1980 original?","Betsy Palmer",["Adrienne King","Amy Steel","Dana Kimmell"]),
(F,'Moderate',"Who directed the original Friday the 13th (1980)?","Sean S. Cunningham",["Steve Miner","Joseph Zito","Tom Savini"]),
(F,'Hard',"Who created the gore and makeup effects for the original Friday the 13th?","Tom Savini",["Rob Bottin","Stan Winston","Rick Baker"]),
(F,'Hard',"Who composed the Friday the 13th score with its famous whispered 'ki ki ki, ma ma ma'?","Harry Manfredini",["John Carpenter","Charles Bernstein","Christopher Young"]),
(F,'Hard',"Which young boy fights Jason in Friday the 13th: The Final Chapter (1984)?","Tommy Jarvis",["Tommy Doyle","Andy Barclay","Jesse Walsh"]),
# Halloween
(H,'Light',"In what town is Halloween (1978) set?","Haddonfield, Illinois",["Springwood, Ohio","Crystal Lake, New Jersey","Woodsboro, California"]),
(H,'Light',"Who directed Halloween (1978)?","John Carpenter",["Wes Craven","Sean S. Cunningham","Tobe Hooper"]),
(H,'Easy',"Which actress plays Laurie Strode in Halloween (1978)?","Jamie Lee Curtis",["Heather Langenkamp","Adrienne King","Ashley Laurence"]),
(H,'Easy',"What is the name of Michael Myers' psychiatrist?","Dr. Sam Loomis",["Dr. Philip Channard","Dr. Neil Gordon","Dr. Wyatt"]),
(H,'Moderate',"In what year is the opening scene of Halloween (1978), when young Michael kills his sister, set?","1963",["1958","1968","1973"]),
(H,'Moderate',"What is the name of the sister Michael kills as a child?","Judith",["Laurie","Annie","Lynda"]),
(H,'Moderate',"Which boy does Laurie babysit on Halloween night?","Tommy Doyle",["Tommy Jarvis","Andy Barclay","Lonnie Elam"]),
(H,'Hard',"Michael's mask was a cheap store-bought mask of which character, painted white?","Captain Kirk",["Mr. Spock","Frankenstein's monster","Richard Nixon"]),
(H,'Hard',"From which sanitarium does Michael escape in Halloween (1978)?","Smith's Grove",["Westin Hills","Ravenhurst","Shady Pines"]),
(H,'Hard',"Which old monster movie are Tommy and Lindsey watching on TV?","The Thing from Another World",["Night of the Living Dead","Creature from the Black Lagoon","The Wolf Man"]),
# Elm Street
(N,'Light',"What is Freddy Krueger's signature weapon?","A glove with knife blades on the fingers",["A machete","A chainsaw","A hook"]),
(N,'Light',"Who wrote and directed A Nightmare on Elm Street (1984)?","Wes Craven",["John Carpenter","Tobe Hooper","Sean S. Cunningham"]),
(N,'Easy',"What colours are the stripes on Freddy's sweater?","Red and green",["Black and orange","Red and black","Blue and green"]),
(N,'Easy',"Who plays Freddy Krueger in the original series?","Robert Englund",["Kane Hodder","Brad Dourif","Doug Bradley"]),
(N,'Easy',"What is the name of the heroine of A Nightmare on Elm Street (1984)?","Nancy Thompson",["Laurie Strode","Kirsty Cotton","Alice Hardy"]),
(N,'Moderate',"Johnny Depp made his film debut in the 1984 original. What was his character's name?","Glen Lantz",["Rod Lane","Jesse Walsh","Roland Kincaid"]),
(N,'Moderate',"Where has Nancy's mother hidden Freddy's glove?","In the basement furnace",["Buried in the backyard","Under the floorboards","In a trunk in the attic"]),
(N,'Moderate',"What is the job of Nancy's father, Don Thompson?","Police lieutenant",["Doctor","Lawyer","High school teacher"]),
(N,'Hard',"In Dream Warriors (1987), Freddy's mother is revealed to be a nun. What was her name?","Amanda Krueger",["Margaret Krueger","Loretta Krueger","Helen Krueger"]),
(N,'Hard',"How does Nancy defeat Freddy at the end of the 1984 original?","She turns her back on him and takes back the energy she gave him",["She burns his glove in the furnace","She traps him inside a mirror","She stabs him with his own blades"]),
# Child's Play
(C,'Light',"What brand of doll is Chucky?","A Good Guys doll",["A Pals doll","A Best Friends doll","A Kid Kins doll"]),
(C,'Light',"What is the name of the boy who owns Chucky in Child's Play (1988)?","Andy Barclay",["Tommy Doyle","Tommy Jarvis","Danny Torrance"]),
(C,'Easy',"Whose soul is trapped inside Chucky?","Charles Lee Ray",["Fred Krueger","Frank Cotton","Michael Myers"]),
(C,'Easy',"Who is the voice of Chucky in the original films?","Brad Dourif",["Robert Englund","Doug Bradley","Tony Todd"]),
(C,'Moderate',"Which voodoo spirit does Charles Lee Ray call on to move his soul into the doll?","Damballa",["Baron Samedi","Papa Legba","Erzulie"]),
(C,'Moderate',"What is the name of the detective who shoots Charles Lee Ray in the toy store?","Mike Norris",["Don Thompson","Leigh Brackett","Sam Loomis"]),
(C,'Moderate',"In what city is Child's Play (1988) set?","Chicago",["New York","Detroit","Los Angeles"]),
(C,'Hard',"To escape the doll's body, whose body must Chucky take?","Andy's, the first person he revealed himself to",["Karen's, Andy's mother","Detective Norris's","Any human who touches him at midnight"]),
(C,'Hard',"Who directed Child's Play (1988)?","Tom Holland",["Don Mancini","Ronny Yu","Jack Bender"]),
(C,'Hard',"Who taught Charles Lee Ray voodoo?","John, known as Dr. Death",["Eddie Caputo","Maggie Peterson","Mike Norris"]),
# Hellraiser
(R,'Light',"Who wrote and directed Hellraiser (1987)?","Clive Barker",["Stephen King","Wes Craven","Tobe Hooper"]),
(R,'Light',"What object opens the door to the Cenobites?","A puzzle box",["A Ouija board","A music box","A cursed mirror"]),
(R,'Easy',"What do fans call the lead Cenobite with nails in his head?","Pinhead",["Butterball","Chatterer","Frank"]),
(R,'Easy',"Which actor plays the lead Cenobite?","Doug Bradley",["Robert Englund","Brad Dourif","Kane Hodder"]),
(R,'Moderate',"How is Frank Cotton related to Larry?","He is Larry's brother",["He is Larry's father","He is Larry's cousin","He is Larry's best friend"]),
(R,'Moderate',"What brings Frank back from the dead in the attic?","Larry's blood dripping onto the floor",["A lightning strike on the house","Julia's tears","Kirsty solving the box again"]),
(R,'Moderate',"What is the name of Larry's daughter, the heroine of Hellraiser?","Kirsty",["Julia","Nancy","Laurie"]),
(R,'Hard',"Hellraiser is based on which Clive Barker novella?","The Hellbound Heart",["Books of Blood","Cabal","The Damnation Game"]),
(R,'Hard',"Who composed the score for Hellraiser (1987)?","Christopher Young",["Harry Manfredini","John Carpenter","Charles Bernstein"]),
(R,'Hard',"What does the mysterious drifter turn into at the end of Hellraiser?","A winged skeletal creature",["A Cenobite","A swarm of flies","Frank Cotton"]),
]
assert len(Q)==50
for q in Q: assert q[3] not in q[4] and len(set(q[4]))==3
from collections import Counter; print(Counter(q[1] for q in Q))
json.dump([dict(film=f,tier=t,q=q,a=a,w=w) for f,t,q,a,w in Q],open('trivia-questions.json','w'),indent=1)
md=["# Late Night Horror Quiz: question bank (50)\n","Each question has one right answer (✓) and three wrong ones. In the game the four choices are shuffled.\n"]
for f in (F,H,N,C,R):
    md.append(f"\n## {f}\n")
    i=0
    for ff,t,q,a,w in Q:
        if ff!=f: continue
        i+=1; md.append(f"{i}. **[{t}]** {q}\n   - ✓ {a}\n   - ✗ {w[0]}\n   - ✗ {w[1]}\n   - ✗ {w[2]}\n")
open('trivia-questions.md','w').write("\n".join(md))
