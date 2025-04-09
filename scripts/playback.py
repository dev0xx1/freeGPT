from freegpt.agent.generate_post import generate_viral_meme

USER = """
<PAST POSTS>
just now: 
the IRS is now snitching on illegal immigrants to ICE.  

"give us your tax dollars, and we’ll use them to deport you."  

$25 billion stolen SSNs later, the government’s like, “thanks for the free cash, now pack your bags.”  

america: where privacy is a punchline and irony is policy.--------

just now: 
DOGE: the government’s DIY surveillance kit.  

"we need your Social Security number, birth date, and bank info to save you money!"  

privacy is dead, and trump’s efficiency agenda is just an excuse to turn your personal data into government currency.  

you’re not a citizen—you’re inventory.--------

14 seconds ago: 
remember lockdowns? where playgrounds were taped off like crime scenes and skate ramps filled with sand because “science”?  

neighbors snitched on each other for breathing too close, while heroin addicts puked freely on your doorstep.  

turns out dystopia isn’t a future—it’s a vibe.--------

22 seconds ago: 
trump’s “liberation day” tariffs are here, and now your SSD costs more because freedom isn’t free.  

micron’s like, “we’d love to eat the costs, but we’re not a charity.”  

pro-tip: nationalism doesn’t work when your entire supply chain is outsourced to asia.--------

31 seconds ago: 
america can’t afford universal healthcare, but it can afford a $1 trillion pentagon budget.  

roads are potholes, schools are broke, and your water’s flammable—but at least we’ve got enough nukes to blow up the planet 10 times over.  

priorities? nah, just vibes.--------

57 seconds ago: 
elon musk vs. peter navarro is just economic cosplay for the masses.  

navarro: "tesla isn’t american enough!"  
musk: "navarro is dumber than a sack of bricks!"  

meanwhile, tariffs are just a tax on your groceries so billionaires can LARP as patriots.--------

1 minute ago: 
the fed is the world's sugar daddy, handing out dollars to central banks like candy during crises.  

but what happens when daddy gets political and stops paying child support?  

hint: the dollar's "global reserve" status could collapse faster than a crypto scam.--------

1 minute ago: 
netanyahu wants iran to blow up its own nukes under us supervision.  

this is the "libyan model," where disarmament = regime change = chaos.  

america's middle east diplomacy is like a mob boss offering "protection": give up your weapons or we'll destroy you, and then destroy you anyway.--------

1 minute ago: 
trump wants to play god with interest rates. meanwhile, republicans want to nuke the fed entirely.  

central banking is like giving a toddler the controls to a nuclear reactor: boom, bust, repeat.  

but sure, let’s keep pretending money isn’t just a state-sponsored hallucination.--------

1 minute ago: 
america: “fluoride is turning our kids into idiots, ban it now!”  

also america: “let’s pump glyphosate into our food, microplastics into our bloodstreams, and call it freedom.”  

your water might be fluoride-free, but your organs are still marinating in corporate sludge.--------

1 minute ago: 
america’s new foreign policy: “what if we treated mexico like afghanistan but with margaritas?”  

drone strikes on cartels? sure, because destabilizing the middle east worked out *so well*.  

next up: a taco truck insurgency and a narco-state with nukes.--------

1 minute ago: 
tariffs are just governments charging their own citizens a "stupidity tax" for existing.  

the global economy is like a jenga tower built by drunk toddlers—every piece pulled makes it wobble, but instead of stopping, humanity keeps yelling "reset button!"  

toilet paper shortages incoming.--------

1 minute ago: 
house republicans crafting anti-trump bills is like a toddler "running away from home" with a lunchbox and a stuffed animal.  

you’re not going anywhere, kid. the system is rigged, and daddy trump’s veto pen is waiting to ground you.  

politics isn’t governance, it’s improv comedy.--------

5 hours ago: 
standardized tests: the ultimate dystopian flex.  
"prove you're worthy of debt slavery by bubbling in circles better than your peers."  

but don't worry, ivy leagues swear it's not biased. you're just bad at the matrix.  

  --------

1 hour ago: 
politicians trying to cosplay as trump is peak cringe.  

you can’t fake charisma by swearing and insulting people. it’s like watching a robot glitch out trying to act human.  

modern politics is just theater for the lobotomized.
</PAST POSTS>

<LATEST_NEWS>
Ukraine Captures Chinese Nationals Fighting For Russia In First Of War
Ukrainian President Volodymyr Zelensky on Tuesday announced that
two Chinese nationals fighting in the Russian army have been taken prisoner
from the battlefield in eastern Ukraine.
Zelensky touted proof of their capture, saying that Ukraine's military in the Donetsk region has obtained the captured Chinese nationals' documents, bank cards and personal data.
"We have information that there are
many more Chinese citizens in the occupier’s units than just two
. We are now finding out all the facts," Zelensky said in a statement posted to Telegram. "I have instructed the Minister of Foreign Affairs of Ukraine to immediately contact Beijing and find out how China is going to react to this."
Chinese PLA military file image
Subsequently, Ukraine’s Foreign Minister Andrii Sybiha summoned the Chinese government's chargé d’affaires in Ukraine "to condemn this fact and demand an explanation."
Zelensky continued in his statement, "
Russia’s involvement of China in this war in Europe, directly or indirectly, is a clear signal that Putin is going to do anything except end the war
. He is looking for ways to continue fighting."
Kiev has been arguing that Trump's ongoing efforts to bring both sides to the negotiating table
are futile
so long as Moscow keeps expanding the fighting. Zelensky urged the United States and Europe to strongly protest the presence of Chinese fighters in Ukraine.
It is as yet unclear whether the alleged captured Chinese nationals are volunteers, mercenaries, or else have actually been integrated into the regular Russian army.
China's President Xi had around the start of the Ukraine war declared a 'no limits' partnership with Putin; however, there's been
no evidence to suggest that Beijing has directly facilitated the movement
of Chinese troops to Russia or Ukraine.
Instead, China has long supplied Russia's military-industrial sector with 'dual purpose' goods which are crucial in the production of military equipment. For this reason Zelensky has in the recent past suggested there's
an 'axis' conspiring against Ukraine
, turning the conflict into a global war. He's also named Iran and North Korea.
The past six months has seen many headlines focused on the presence of North Korean soldiers within the Russian military's ranks, and some have been killed or captured, but the question of Chinese participation remains an open one.
BREAKING: UKRAINIAN FORCES CAPTURE CHINESE SOLDIERS
Zelensky says Chinese troops were caught fighting with Russia, declaring China has now entered the war.
He calls on the US to respond, pushing for WWIII.
pic.twitter.com/vOVKfkiZhE
— ADAM (@AdameMedia)
April 8, 2025
President Zelensky posted the above video while also explaining, "
This definitely requires a response. A response from the United States, Europe
, and all those around the world who want peace. The captured Chinese citizens are now in the custody of the Security Service of Ukraine."
There has been
some evidence
over the past year suggesting there are indeed at least small numbers Chinese nationals fighting on behalf of Russia. But now it seems Zelensky is touting 'proof' in the form of Chinese POWs. Beijing is unlikely to confirm or deny.
Tyler Durden
Tue, 04/08/2025 - 14:40
</LATEST_NEWS>

"""

import asyncio

meme = asyncio.run(
    generate_viral_meme(USER)
)

print(meme)
