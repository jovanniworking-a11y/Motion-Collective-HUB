"""Vision board data · prices as of 1 Oct 2026 (from the research agents; re-check at checkout)."""
ZONES = [
 ("floor", "Dance floor", "Decks, rug, mirror ball"),
 ("bar", "Bar · island", "Batch, cups, candles"),
 ("walls", "Walls", "Prints, frames, mirror"),
 ("witch", "Witchy details", "Drape, florals, red bulbs"),
 ("balcony", "Balcony", "Smoking spot"),
]
# id, zone, name, store, price (None = varies), spec, why, url, obj (3D key or None), pick, cart (lean/full/both/None)
ITEMS = [
 ("rug-target","floor","Leopard woven rug, black/white 5×7","Target · Threshold",70.00,"Low pile, 5'×7'","Black and white reads gallery, not costume. Sits under the decks and marks the booth.","https://www.target.com/p/daffodil-leopard-print-woven-rug-threshold/-/A-54307551","rug",True,"full"),
 ("rug-garvee","floor","Leopard patchwork rug, brown 5×7","Garvee",50.99,"Washable, 0.23\" pile, non-slip","Cheapest washable option. Spills wash out.","https://www.garvee.com/products/garvee-area-rug-washable-leopard-print-5x7-brown-pho-34uua6ht","rug",False,"lean"),
 ("rug-well","floor","Mid-century leopard flatweave, brown","Walmart · Well Woven",93.98,"5'×7' flatweave","More designed pattern, muted.","https://www.walmart.com/ip/Well-Woven-Animal-Prints-Leopard-Mid-Century-Modern-Leopard-Pattern-Brown-Flat-Pile-Easy-to-Clean-7-10-x-9-10-Area-Rug/5626972514","rug",False,None),
 ("ball-rent","floor","Rent: 20\" mirror ball + motor + pin light","Miscellaneous Rentals · E 51st St",45.00,"Pick up at HQ, return after","Bigger and cheaper than buying a full kit.","https://www.miscaustin.com/av-lighting/p/discomirror-ball","disco",True,None),
 ("ball-16","floor","16\" mirror ball","BalsaCircle",69.99,"Foam core, glass tiles","If you'd rather own one.","https://balsacircle.com/products/16-in-wide-glass-hanging-party-disco-mirror-ball","disco",False,None),
 ("ball-2x12","floor","2 × 12\" mirror balls","BalsaCircle",55.99,"Foam core, hanging ring","Cheapest way to get a ball.","https://balsacircle.com/products/2-pcs-12-inch-large-silver-mirror-disco-balls","disco",False,"lean"),
 ("motor","floor","Battery mirror-ball motor, 5 RPM","Efavormart",16.49,"3×AA, ~12 h, up to 20\"","Only needed if you buy a ball. Tape over its LEDs.","https://www.efavormart.com/products/led-light-rotating-heavy-duty-motor-for-hanging-mirror-disco-ball-5-rpm-battery-operated-motor-with-8-hanging-chain","disco",False,"lean"),
 ("disp-acrylic","bar","3 gal acrylic dispenser with ice core","WebstaurantStore · Choice",42.99,"Shatterproof, ice core","Holds the 2 gal batch with room. Ice core keeps it cold without watering it down.","https://www.webstaurantstore.com/choice-3-gallon-acrylic-beverage-dispenser-with-ice-core-and-fruit-infuser/176ACB3INFV.html","dispenser",True,"full"),
 ("disp-glass","bar","2 gal glass dispenser","Target · Threshold",29.75,"Glass, steel spigot","Cheapest. Glass with 70 people is a risk.","https://www.target.com/p/2gal-glass-modern-beverage-dispenser-threshold-8482/-/A-51808235","dispenser",False,"lean"),
 ("disp-tc","bar","2 gal glass dispenser, industrial","WebstaurantStore · TableCraft",57.49,"Glass, ice core","Best-looking glass one. Add the black riser ($13.49).","https://www.webstaurantstore.com/tablecraft-10090-industrial-collection-2-gallon-glass-beverage-dispenser-with-infuser-ice-core/80810090.html","dispenser",False,None),
 ("cups","bar","Clear 16 oz cups × 3 packs (150)","Target · Dealworthy",14.97,"PET, $4.99 per 50","Clear only, per the cup rule.","https://www.target.com/p/clear-disposable-cups-16-fl-oz-50ct-dealworthy-8482/-/A-89685923","cups",True,"full"),
 ("tapers","bar","Black LED taper candles, 4-pack","Walmart",23.78,"Real wax, flicker, remote","Witchy without an open flame in an apartment.","https://www.walmart.com/ip/6-5-Inch-Printed-Flameless-Candle-Real-Wax-Black-LED-Taper-Candles-with-Remote-Control-for-Weddings-Home-Decoration-Christmas-Pack-of-4/5888801755","tapers",True,"full"),
 ("prints","walls","Eye triptych, 3 × 24×36 posters","Walgreens · FedEx Guadalupe · Mpix",68.58,"Walgreens code NICEDECO −70% until 3 Oct","The flyer's three eyes, stacked on the wall the crowd faces.","https://photo.walgreens.com/store/posters","prints",True,"full"),
 ("frame","walls","Ornate antique-black frame 18×24","Target · Craig Frames",60.99,"Wood, glass","Frame the middle eye only. One is enough.","https://www.target.com/p/ancient-ornate-18x24-inch-antique-black-picture-frame/-/A-93362451",None,False,None),
 ("mirror","walls","24\" round baroque mirror, black","Walmart · YIDIE",55.99,"Ornate metal frame","Over the TV. Catches the mirror ball.","https://www.walmart.com/ip/17687955004","mirror",False,None),
 ("borrow","walls","Borrow 2–3 local pieces","Open Canopy · Sat 3 Oct, 1–4pm",None,"916 Springdale Rd","Meet artists at open studios. Offer a wall credit, IG tag and an invite.","http://www.canopyaustin.com/",None,True,None),
 ("drape","witch","Black sheer cloth 197×79\"","Walmart · AGCAN",15.99,"One large gauze piece","Over the hall windows. Darkens the room and reads witchy.","https://www.walmart.com/ip/AGCAN-Halloween-Creepy-Cloth-Decoration-Black-Gauze/16711302118","drape",True,"full"),
 ("eucalyptus","witch","Black eucalyptus stems, 20","eBay",30.59,"Faux, ships 3–6 days","Black branches in a vase on the island.","https://www.ebay.com/itm/318893369213","eucalyptus",True,"full"),
 ("bulbs","witch","Red filament bulbs, 2-pack","Home Depot · Sunlite",14.99,"E26, dimmable","Swap into the bedroom-hall lamps. Brand red.","https://www.homedepot.com/p/Sunlite-60-Watt-Equivalent-A19-Dimmable-Filament-E26-Medium-Base-LED-Light-Bulb-in-Red-2-Pack-HD02271-1/312593834",None,True,"full"),
 ("ashtray","balcony","Windproof lidded ashtray, black","Walmart · XTORKIT",11.82,"Steel, weighted, size M","One tray, under a light.","https://www.walmart.com/ip/Windproof-Lid-Smokeless-Odor-Control-Outdoor-Ashtray-Stainless-Steel-Cigarette-Ash-Holder-Patio-Yard-Home-Balcony-Heavy-Duty-Decorative-Tabletop-Blac/20489255604","ashtray",True,"both"),
 ("sign","balcony","Smoking sign","Print our own",None,"Bodoni, 5×7","A printed sign in the flyer font beats a hardware-store sign.",None,"ashtray",True,None),
]
PLACES = [  # route order from West Campus
 ("FedEx Office, Guadalupe","2711 Guadalupe St","Drop the 24×36 files before noon; same-day posters.","https://local.fedex.com/en-us/tx/austin/office-0122/banners-signs-posters"),
 ("Room Service Vintage","117 E North Loop Blvd","Statement lamps, art glass, frames. Daily 10am–8pm.","https://roomservicevintage.com/"),
 ("Top Drawer Thrift","5312 Airport Blvd","Cheap frames, mirrors, leopard textiles, candlesticks.","https://www.topdrawerthrift.org/"),
 ("Miscellaneous Rentals","1901 E 51st St","Reserve the 20\" mirror ball ($45) for pickup the week of the 30th.","https://www.miscaustin.com/av-lighting/p/discomirror-ball"),
]
EXTRA_PLACES = [
 ("Uncommon Objects","1602 Fortview Rd","Best for ornate mirrors and candelabras. Daily 10–6.","https://www.uncommonobjects.com/"),
 ("City Alchemist","1105 E 6th St","Witch shop: candles, curios. Daily 12–7.","https://www.cityalchemist.co/"),
 ("Spirit Halloween","2525 W Anderson Ln","LED bulbs, faux candelabras. Seasonal.","https://stores.spirithalloween.com/tx/austin/halloween-store-60741.html"),
 ("Open Canopy","916 Springdale Rd","Open studios Sat 3 Oct 1–4pm. Borrow art.","http://www.canopyaustin.com/"),
]
