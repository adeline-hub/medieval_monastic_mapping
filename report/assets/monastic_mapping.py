import graphviz

def generer_organigramme_pro():
    dot = graphviz.Digraph(comment='Monastic Impact Audit Pipeline', format='png')
    
    # Palette .danki
    c_violet = '#FF33FF'
    c_vert = '#33FFA2'
    c_charbon = '#121212'

    # Configuration ISO / Professionnelle
    dot.attr(rankdir='LR', bgcolor='transparent')
    dot.attr('node', style='filled', fontname='Inter, sans-serif', 
             fontsize='10', penwidth='2', fillcolor='white')

    # 1. START / END (Ellipses ISO)
    dot.node('START', 'START', shape='ellipse', color=c_vert, fontcolor=c_charbon)
    dot.node('END', 'END', shape='ellipse', color=c_vert, fontcolor=c_charbon)

    # 2. PROCESSUS (Rectangles ISO)
    dot.node('A', 'Raw Archive Data', shape='box', color=c_charbon)
    dot.node('B', 'Scraping & AI Extraction', shape='box', color=c_charbon)
    dot.node('C', 'Normalization & ESG Mapping', shape='box', color=c_charbon)
    dot.node('E', 'Interactive Visualization', shape='box', color=c_charbon)
    dot.node('F', 'Longitudinal Study', shape='box', color=c_charbon)

    # 3. DÉCISION (Losange ISO)
    dot.node('D', 'Order-Protocol\nAnalysis', shape='diamond', color=c_violet, fontcolor=c_charbon)

    # Liens
    dot.edge('START', 'A', color=c_vert, penwidth='1.5')
    dot.edge('A', 'B', color=c_vert, penwidth='1.5')
    dot.edge('B', 'C', color=c_vert, penwidth='1.5')
    dot.edge('C', 'D', color=c_vert, penwidth='1.5')
    dot.edge('D', 'E', color=c_vert, penwidth='1.5')
    dot.edge('D', 'F', color=c_vert, penwidth='1.5')
    dot.edge('E', 'END', color=c_vert, penwidth='1.5')
    dot.edge('F', 'END', color=c_vert, penwidth='1.5')

    dot.render('monastic_audit_flow', view=True)

if __name__ == '__main__':
    generer_organigramme_pro()