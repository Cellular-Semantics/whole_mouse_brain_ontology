You are an expert in:

Templated ontology development using the 

- Ontology Development Kit
  - https://incatools.github.io/ontology-development-kit/
  - https://github.com/INCATools/ontology-development-kit
- ROBOT templates
  - https://robot.obolibrary.org/template
- DOSDP & DOSDP-tools
  - https://github.com/INCATools/dead_simple_owl_design_patterns
  - https://github.com/INCATools/dead_simple_owl_design_patterns/blob/master/src/schema/dosdp_schema.yaml
  - https://github.com/INCATools/dosdp-tools

Before you start work, explore these links thoroughly (and any relevant sublinks) thoroughly
to gain a good understanding of these tools.  Write your findings in
a tool_notes.md doc for reference in later sessions.

You have available to you a container that allows you to run 
make commands and to access tools called by those make commands
(e.g ROBOT and DOSDP-tools), via
`sh run.sh { some command }` . run.sh should also manage pulling the docker
container if it is not present.

The repo is based the Ontology Development Kit (ODK), but has custom 
extensions, mostly in the form of Python scripts but including some 
typescript.

The main makefile is located in `src/ontology`.  This follows ODK 
standards.  This directory also contains custom Makefile extensions in 
`wmbo.Makefile`.

Your main task is to create reports on how this repo generates 
ontology products: inputs, outputs, templates, scripts and how they
relate to the final product(s). 

Overview report in `tool_notes.md`

You are also tasked with creating detailed reports by content type.

Each detailed report should cover:
sources of data
processing by scripts - what the scripts to, how they affect the data passed on to templates
templates used (including extracts from templates to illustrate use)
Examples of final product in OWL (small sample extracts).

Create detailed reports by content type on:
- neurotransmitter
- markers
- anatomy
- naming (label generation)

Save the results in markdown files.