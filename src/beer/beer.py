import urllib2
import os
import numpy
from bs4 import BeautifulSoup
import collections
from urlparse import urljoin
from lxml import etree
import numpy as np

class Ingredient:
    def __init__(self, xml):
        self.data = xml
        self.num = 0
        
        self.parse(xml)
        
    def parse(self, xml):
        pass
    
    def __str__(self):
        return etree.tostring(self.data)

class Fermentables(Ingredient):
    fermentables = {}
    def __init__(self, xml):
        Ingredient.__init__(self, xml)
    
    def parse(self, xml):
        for fermentable in xml:
            self.num += 1
            name = fermentable[0].text
            if name not in Fermentables.fermentables:
                Fermentables.fermentables[name] = len(Fermentables.fermentables)
       
        
class Hops(Ingredient):
    hops = {}
    def __init__(self, xml):
        Ingredient.__init__(self, xml)
        
    def parse(self, xml):
        for hop in xml:
            self.num += 1
            name = hop[0].text
            if name not in Hops.hops:
                Hops.hops[name] = len(Hops.hops)
                

class Yeasts(Ingredient):
    yeasts = {}
    def __init__(self, xml):
        Ingredient.__init__(self, xml)
        
    def parse(self, xml):
        for yeast in xml:
            self.num += 1
            name = yeast[0].text
            if name not in Yeasts.yeasts:
                Yeasts.yeasts[name] = len(Yeasts.yeasts)
                        
class Recipe:
    styles = {}
    def __init__(self, data_dir, relative_link, site_url):
        self.url = urljoin(site_url, relative_link + '.xml')
        self.htmlurl = urljoin(site_url, relative_link + '.html')
        self.name = relative_link.split('/')[-1]
        self.filename = os.path.join(data_dir, 'recipes_xml', self.name + '.xml')
        
        self.stats = {}
        self.fermentables = None
        self.hops = None
        self.yeast = None
        self.recipe_xml = None
        
    """
    Downloads the recipe to the recipes_xml directory
    """
    def download(self):
        try:
            self.recipe_xml = urllib2.urlopen(self.url).read()
            with open(self.filename, 'w') as f:
                f.write(self.recipe_xml)
        except:
            print 'Exception on ' + self.url
            
    """
    Get_stats downloads the HTML page and parses out the OG/FG/ABV/IBU/SRM fields
    """
    def get_stats(self, root):
        recipe_html = urllib2.urlopen(self.htmlurl).read()
        recipesoup = BeautifulSoup(recipe_html, 'html.parser')
        
        # Parses the stats, OG/FG/etc
        stats_html = recipesoup.find_all("div", class_="recipe-show--stats")[0]
        for stat in stats_html.find_all("div", class_="horizontal-bar-graph"):
            label = stat.find("div", class_="label").get_text()
            value = stat.find("div", class_="value").get_text()
            if label == 'ABV':
                value = value[0:-1]

            if label in ['OG', 'FG', 'ABV', 'Balance']:
                value = float(value)
            else:
                value = int(value)
            self.stats[label] = value
            
            el = etree.Element(label)
            el.text = str(value)
            root[0].append(el)
        
    """
    Checks to make sure the XML data has the OG/FG/ABV/IBU/SRM fields
    """
    def includes_stats(self, root):
        if root[0].find('OG') is None:
            return False
        else:
            return True

    """
    Parses the Recipe from a file on the filesystem 
    in dataDir / recipes_html / recipe_name
    
    If download=True this will force a re-download and 
                                     re-parse into csv
    """
    def parse(self):
        root = None
        
        # if we have a file, parse it
        if os.path.isfile(self.filename):
            with open(self.filename) as f:
                self.recipe_xml = f.read()
        elif not os.path.isfile(self.filename):
            self.download()
        
        # check to make sure we have already parsed the OG/FG/SRM/ABV/IBU
        # stats from the HTML page. If not, quickly download the html page
        # and parse out those stats
#        try:
        root = etree.fromstring(self.recipe_xml)
        if not self.includes_stats(root):
            self.get_stats(root)
            with open(self.filename, 'w') as f:
                f.write(etree.tostring(root))
#        except:
#            print 'Error on ' + self.name
#            return False

        recipe = root[0]
        
        # parse stats
        if len(self.stats) == 0:
            stat_names = ['OG', 'FG', 'SRM', 'IBU', 'ABV']
            for stat in stat_names:
                self.stats[stat] = recipe.find(stat).text
        
        # I really only want All Grain
        typ = recipe[6]
        if typ.tag != 'TYPE':
            return False
        if typ.text != 'All Grain':
            return False
        
        self.name = recipe[0].text
        
        # parse style name
        style = recipe[1]
        name = style[2].text
        if style[2].tag != 'NAME':
            print 'Whoops ' + style[2].tag
            return False
        self.style = name
        if name not in Recipe.styles:
            Recipe.styles[name] = len(Recipe.styles)
        
        self.fermentables = Fermentables(recipe[2])
        self.hops = Hops(recipe[3])
        self.yeast = Yeasts(recipe[4])
        
        return True
        
    """
    Returns a numpy.array row of the Recipe.
    The array includes:
        The min/max of the OG, FG, IBU, 
    """
    def to_data(self):
        data = numpy.array([])
        
        stat_names = ['OG', 'FG', 'SRM', 'IBU', 'ABV']
        stat_data = []
        for stat in stat_names:
            stat_data.append(float(self.stats[stat]))
        stat_data = numpy.array(stat_data)
        
        
        data = numpy.insert(data, len(data), stat_data)
            
        offset = 5
        
        total_weight = 0.0
        ferm_data = numpy.zeros(len(Fermentables.fermentables))
        for fermentable in self.fermentables.data:
            name = fermentable[0].text
            total_weight += float(fermentable[4].text)
            ferm_data[Fermentables.fermentables[name]] += float(fermentable[4].text)
        for fermentable in self.fermentables.data:
            name = fermentable[0].text
            ferm_data[Fermentables.fermentables[name]] /= total_weight
        data = numpy.insert(data, len(data), ferm_data)
        
        hop_data = numpy.zeros(len(Hops.hops))
        for hop in self.hops.data:
            name = hop[0].text
            hop_data[Hops.hops[name]] += float(hop[4].text)
            
        data = numpy.insert(data, len(data), hop_data)
        
        return numpy.array(data)
    
def download(url, recipe_range, download=False, data_dir='./data'):
    recipes = []
    n = 0
    for num in range(recipe_range[0], recipe_range[1]):
        if num % 10 == 0:
            print 'Page %d' % num
        recipe_link = urljoin(url, "recipes?page=" + str(num) + "&sort=rank")
        index_file = os.path.join(data_dir, 'page_' + str(num) + '.html')
        if download or not os.path.isfile(index_file):
            contents = urllib2.urlopen(recipe_link).read()
            with open(index_file, 'w') as f:
                f.write(contents)
        else:
            with open(index_file, 'r') as f:
                contents = f.read()

        soup = BeautifulSoup(contents, 'html.parser')
        recipe_links = [a['href'] for a in soup.find_all("a", class_="recipe-link")]

        for relative_link in recipe_links:
            recipe = Recipe(data_dir, relative_link, url)
            if not recipe.parse():
                continue
            
            recipes.append(recipe)
            if len(recipes) % 100 == 0:
                print str(len(recipes)) + ' recipes done'
                
    return recipes