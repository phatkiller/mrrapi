import mrrapi

mkey = 'YourKey'
msecret = 'YourSecret'

mapi = mrrapi.api(mkey,msecret)
debug = False

def parsemyrigs(rigs,list_disabled=False):
    """
    :param rigs: pass the raw api return from mrrapi.myrigs()
    :param list_disabled: Boolean to list the disabled rigs
    :return: returns dict by algorithm
    """
    global mrrrigs
    mrrrigs = {}
    # I am not a python programmer, do you know a better way to do this?
    # first loop to create algo keys
    # second loop populates rigs in algo
    for x in myrigs['data']['records']:
        mrrrigs.update({str(x['type']): {}})
    for x in myrigs['data']['records']:
        #print x
        if list_disabled or  str(x['status']) != 'disabled':
            mrrrigs[str(x['type'])][int(x['id'])] = str(x['name'])
    return mrrrigs

def calculateMaxIncomeAlgo(parsedrigs):
    global mhash
    rentalfee = float(0.03)
    outcome = float(0)
    mhash = float(0)

    namelen = 0

    # Pre-process loop
    for algo in parsedrigs:
        algorigs = parsedrigs[algo]
        for x in algorigs:
            nametmp = len(parsedrigs[algo][x])
            if nametmp > namelen:
                namelen = nametmp
            #print x, algo, namelen
    layout = "{0:>" + str(namelen) + "}{1:>10}{2:>10}{3:>14}{4:>12}{5:>15}{6:>14}"
    print(layout.format("  Device Name  ", " Type ", " Speed ","Cur hash 30m","Price  ", "Daily income", "Rented? "))

    for algo in parsedrigs:
        algorigs = parsedrigs[algo]
        for x in algorigs:
            rig = mapi.rig_detail(x)
            t = rig['data']
            if debug:
                print t
            rigstat = "available"
            curhash = float(0.0)
            mhashrate = float(float(t['hashrate']['advertised'])/(1000000.0))
            mhash += mhashrate
            dailyprice = mhashrate * float(t['price']) * (1.0 - rentalfee)
            mhunit = "MH"
            if 1000 <= mhashrate < 1000000:
                mhunit = "GH"
                mhashrate = float(mhashrate/1000)
            elif mhashrate >= 1000000:
                mhunit = "TH"
                mhashrate = float(mhashrate/1000000)
            if (str(t['status']) == 'rented'):
                aih = float(t['available_in_hours'])
                rigstat = "R "
                if 0.1 < aih < 10.0:
                    rigstat += " "
                rigstat += str(aih) + " hrs"
            elif (str(t['status']) == 'unavailable'):
                rigstat = "disabled"
            curhash = round(float(t['hashrate']['30min'])/10**6,3)
            print(layout.format(str(t['name']),str(t['type']),str(mhashrate) + " " + mhunit,str(curhash) + " M",str(round(float(t['price']),8)) ,str(round(dailyprice,8)), rigstat))
            outcome += dailyprice

    return outcome

if __name__ == '__main__':
    myrigs = mapi.myrigs()
    if myrigs['success'] is not True:
        print "Error getting my rig listings"
        if str(myrigs['message']) == 'not authenticated':
            print "Make sure you fill in key and secret"
    else:
        prigs = parsemyrigs(myrigs)
        #print prigs
        maxi = calculateMaxIncomeAlgo(prigs)
        print
        print "Max available daily income: " + str(round(maxi,8) - 0.002)

