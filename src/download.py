import beer
import argparse

def getBeers(opts):
    beer = new beer.Beer()
    if beer.dataExists(dataDir):
        beer.loadFromData(dataDir)
    else:
        beer.setUrl("https://www.brewtoad.com")
        beer.downloadBeers(dataDir)
        beer.parseBeers(dataDir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download ")
    parser.add_option("-d", "--data-dir", dest="dataDir",
            help="directory of data/directory to download data to",
            default="data/")
    parser.add_option("-r", "--result-dir", dest="resultDir",
            help="directory of data/directory to output results to",
            default="results/")
    options, args = parser.parse_args()

    print 'Data dir = ' +
