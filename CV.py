import re
import ast
import subprocess

with open("CV.list","r",encoding="utf-8") as f:
    CV = ast.literal_eval(f.read())

CV_header = open("CV_header.html",encoding='utf-8').read().format(
                css=open("CV.css",encoding="utf-8").read(),
                js=open("CV.js",encoding="utf-8").read(),
                email=open("email.js",encoding="utf-8").read()
                )
CV_footer='''
</div>
  </body>
</html>

'''

diploma_template = '''
<section class="diploma" id="{anchor}" data-shortname="{short_name}">
<span class="caret-up-down fa fa-caret-square-o-up"></span>
<span class="caret-up-down fa fa-caret-square-o-down"></span>
<div class="diploma_content">
<h3>{canonical_name}</h3>
<p class="date">{when}</p>
<div style="clear:both;"></div>
<div class="abstract">{abstract}</div>
<div class="full_text">
{text}
</div>
</div>
</section>
'''

skill_template='''
<section class="skill" id="{anchor}" data-shortname="{short_name}">
<span class="caret-up-down fa fa-caret-square-o-up"></span>
<span class="caret-up-down fa fa-caret-square-o-down"></span>
<div class="skill_content">
<h3>{canonical_name}</h3>
<div style="clear:both;"></div>
<div class="abstract">{abstract}</div>
<div class="full_text">
{text}
</div>
</div>
</section>
'''

keyword_template=r'''<span class="keywords"><a href="{link_target}" data-target="{link_target}">{decoration}{link_text}</a>{other_keywords}</span>'''


class CV_item:
    def __init__(self, d):
        '''Create a CV_item from the dictionary d'''
        self.type = d["type"] #One of "diploma", "experience", "skill" or "external_ressource"
        self.names = set([d["name"]])
        self.canonical_name = d["name"]
        try:
            self.short_name = d["shortname"]
        except KeyError:
            self.short_name = self.canonical_name
        try:
            self.names = self.names.union(d["synonyms"])
        except KeyError:
            pass
        try:
            self.sort_key = int(d["sort_key"])
        except KeyError:
            try:
                self.sort_key = int(d["when"][-4:])
            except KeyError:
                self.sort_key = 0
        try:
            self.when = d["when"]
        except KeyError:
            pass
        try:
            self.text = d["text"]
        except KeyError:
            self.text = "<p>FIXME</p>"
            if self.type != "external_ressource":
                print("Empty text")
        else:
            self.text = "<p>"+self.text+"</p>"
            self.text = self.text.replace("\n","</p>\n<p>")
        try:
            self.abstract = d["abstract"]
        except KeyError:
            if self.type != "external_ressource":
                self.abstract = "<p>FIXME</p>"
                print("Empty abstract")
        self.anchor = self.short_name.lower().replace(' ','').replace("'","").replace(',','').replace('/','').replace('+','p')
        try:
            self.target = d["target"] #for type external_ressource
        except KeyError:
            self.target = '#'+self.anchor
        self.links_to = set() #Set of items that talk about self
        return

    def answers_to(self, name):
        return name.lower() in map(lambda x:x.lower(), self.names)

    def talked_about_in(self, item):
        self.links_to.add(item)

    def scan_text(self):
        '''Look for keywords in the text field and refer self to the corresonding items.'''
        for kw in [x for x in KEYWORDS if not self.answers_to(x)]:
            #Without \W, keywords like 'C' would match 'c' in words like cocaine
            #[^\w'+] is to avoid matching "C'est" in french and "C++"
            #s\W is to match the plural forms
            if re.search(r'($|\W)'+re.escape(kw)+r"([^\w'\+]|s\W)", self.text, flags=re.IGNORECASE):
                item_self_talks_about = find_CV_item(kw)
                item_self_talks_about.talked_about_in(self)

    def replacement_text(self, kw_text):
        '''Return the HTML code to write in lieu of kw_text when found in the text of self'''
        if self.answers_to(kw_text):
            return kw_text #No links for e.g. "Python" or a synonym of it in the section about Python
        kw_item = find_CV_item(kw_text)
        if kw_item.type == "external_ressource":
            decoration = '<small><span class="fa fa-external-link"></span></small>'
        else:
            decoration = ""
        other_keywords_links = ""
        for other_item in [x for x in kw_item.links_to if not self.answers_to(x.canonical_name)]:
            other_keywords_links += r'<a href="{target}" data-target="{target}" class="list-group-item">{text}</a>'.format(
                target = other_item.target,
                text = other_item.short_name)
        if other_keywords_links:
            other_keywords_links = '<span class="keyword_list list_group">'+ other_keywords_links + '</span>'
        return keyword_template.format(
            link_target=kw_item.target,
            link_text=kw_text,
            other_keywords=other_keywords_links,
            decoration=decoration)

    def remove_overlapping_spans(self, edits):
        index = 0
        while index < len(edits)-1:
            previous = edits[index]
            current = edits[index+1]
            if previous[0][1] > current[0][0]: #overlapping spans
                if previous[0][1] - previous[0][0] > current[0][1] - current[0][0]:
                    #previous is longer
                    edits.remove(current)
                else:
                    edits.remove(previous)
            else:
                index+=1
        return edits

    def apply_edit_list(self, text, edits):
        '''Return text after modifications specified in edits have been applied'''
        if not edits:
            return text
        if len(edits) > 1:
            edits.sort(key=lambda x:x[0][0]) #Sorting by beginning of span
        if any([x[0][1] > y[0][0] for x,y in zip(edits[:-1],edits[1:])]):
            edits = self.remove_overlapping_spans(edits)
            assert(all([x[0][1] < y[0][0] for x,y in zip(edits[:-1],edits[1:])])) #No overlapping spans
        dot = 0
        modified_text = ""
        for span,replacement_text in edits:
            modified_text += text[dot:span[0]]
            modified_text += replacement_text
            dot = span[1]
        modified_text += text[dot:]
        return modified_text

    def linkify_text(self):
        '''Transform keywords from the text into links.'''
        edit_list = [] #The text must be modified at once, in the end, and not during the loop.
        #Otherwise, keywords will appear in the HTML formating (e.g. href="#objective-c"), and be replaced
        #during a future iteration of the for loop.
        #So we maintain an edit list of pairs [span,replacement_text]
        for kw in KEYWORDS:
            match = re.search(r'(^|\W)('+re.escape(kw)+r")([^\w'\+]|s\W)",
                              self.text,
                              flags=re.IGNORECASE)
            if match:
                corrected_span = [match.span()[0]+len(match.group(1)),
                                  match.span()[1]-len(match.group(3))]
                edit_list.append([corrected_span, self.replacement_text(match.group(2))])
        self.text = self.apply_edit_list(self.text,edit_list)

def find_CV_item(name): #Can be refactored out of existence by making CV_item hashable and CV_items a dict
    #But the hash function must be non trivial enough to handle synonyms
    l = [x for x in CV_items if x.answers_to(name)]
    assert(len(l)==1)
    return l[0]

CV_items = [CV_item(x) for x in CV]
KEYWORDS = set()
for x in CV_items:
    KEYWORDS = KEYWORDS.union(x.names)
for x in CV_items:
    x.scan_text()
for x in CV_items:
    x.linkify_text()

diplomas = [x for x in CV_items if x.type == "diploma"]
diplomas.sort(key=lambda x:x.sort_key)
diplomas.reverse()
skills = [x for x in CV_items if x.type == "skill"]
skills.sort(key=lambda x:x.sort_key)
skills.reverse()
experiences = [x for x in CV_items if x.type == "experience"]
experiences.sort(key=lambda x:x.sort_key)
experiences.reverse()

#Graph generation using the dot language
edges = {}
nodes = {}
for kw in KEYWORDS:
    to_item = find_CV_item(kw)
    nodes['"'+to_item.short_name+'"']=to_item.anchor
    for target in map(lambda x:x.canonical_name,to_item.links_to):
        from_item = find_CV_item(target)
        try:
            edges['"'+from_item.short_name+'"->"'+to_item.short_name+'"'] += 1
        except KeyError:
            edges['"'+from_item.short_name+'"->"'+to_item.short_name+'"'] = 1

with open('CV.dot','w',encoding='utf-8') as f:
    f.write('digraph G {')
    for node in nodes.keys():
        f.write(node+' [href="index.html#'+nodes[node]+'", id="svg_'+nodes[node]+'" target="_top"];\n')
    for edge in edges.keys():
        f.write(edge+' [weight='+str(edges[edge])+'];\n')
    f.write("}")


with open('index.html','w',encoding='utf-8') as f:
    f.write(CV_header)
    f.write('<h2 id="education">Formation, diplômes et récompenses</h2><div style="clear:both;"></div>')
    f.write("\n".join([diploma_template.format(**x.__dict__) for x in diplomas]))
    f.write('<h2 id="skills">Compétences</h2><div style="clear:both;"></div>')
    f.write("\n".join([skill_template.format(**x.__dict__) for x in skills]))
    f.write('<h2 id="experience">Expérience</h2><div style="clear:both;"></div>')
    f.write("\n".join([diploma_template.format(**x.__dict__) for x in experiences]))
    f.write('<h2 id="graph">Sous forme graphique...</h2><div style="clear:both;"></div>')
    f.write(str(subprocess.Popen("dot CV.dot -T svg", shell=True, stdout=subprocess.PIPE).stdout.read(),encoding="utf-8"))

    f.write(CV_footer)

