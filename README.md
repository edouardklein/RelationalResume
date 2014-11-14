# Relational Résumé


This is a Python script to create a résumé whose elements links to each others.

See my résumé to understand quickly what this is about : http://rdklein.fr/CV/

## Main features :

 - Intra-linking : Elements' text is scanned to find words referring to other elements. Those keywords are automatically turned into links. On hover, a list of elements related to the keyword is displayed.
 - Easy PDF generation : To tailor your résumé to a particular offer, choose which elements you want to expand, minimize of simply hide so that you only show what is relevant, and print it (in a PDF file), checking that it fits on one page.
 - Easy to expand : The codebase is concise and easy to build onto. If you want to make fancy things with the data of your résumé (like the graph at the bottom of mine), just code it :) ! Pull requests welcome.


## Usage

Clone the repo :

    https://github.com/edouardklein/RelationalResume.git

Modify file `CV_header.html`, it contains your name, picture and contact information.

Create file `CV.list`, formatted as a Python list of dictionaries. Each dictionary is one element of your résumé (see below).

Generate the contents of the file `email.js` from http://www.jottings.com/obfuscator/ (you don't want your unencrypted email on a web page).


## CV.list syntax
### Example
An element may look like this :
```
{"type":"diploma",
 "name":"PhD in Horribleness",
 "when":"2008",
 "abstract":"Directed by Joss Whedon",
 "text":"More complete description of your work."
 }
```
the `CV.list` file will contain a list of such elements :
```
[
{
"type":"diploma",
 "name":"PhD in Horribleness",
 "when":"2008",
 "abstract":"Directed by Joss Whedon",
 "text":"More complete description of your work."
},
{"type":"experience",
 "name":"Evil league of Evil",
 "when":"2008 onwards",
 "abstract":"Under the supervision of Bad Horse",
 "text":"More complete description of your work."
}
]
```
### Elements fields
#### type
One of `"diploma"`, `"skill"`, or `"experience"`
#### name
Title of the element.
#### when
Only required for elements of type `diploma` or `experience`. The 4 first characters will act as the sort key if none is provided.
#### abstract
One liner explanation about the element.
#### text
Longer description of the element. Will be scanned for keywords (i.e. the names of the other elements.)
#### synonyms
List of strings that, if found in the text of other elements, will link to this one. e.g. `"synonyms":["PhD","doctorate"]` would be found in the entry whose `name` may be `"PhD in Microbiology"`.
#### sort_key
This string will be converted to an int. Higher values will be displayed first.
