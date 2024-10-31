#%%
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
    MarkdownHeaderTextSplitter,
    PythonCodeTextSplitter,
    HTMLHeaderTextSplitter,
    Language,
)

#%%

splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=80,
                add_start_index = True
            )

        
chunks = splitter.create_documents(["""Fishing and aquaculture
The port of Taranto hosts numerous fishing boats. The fleet is mainly made up of about 80 fishing boats, which do not exceed 10 gross tonnage and which practice trawling, while the remaining small-scale fishing boats operate with gillnets. The sea, rich and generous, is populated by dentex, sea bream, glit-head bream, grouper, redfish, mullet, mussels, sea urchin, anchovies, shrimp and squid. Other significant fishing ports are Manfredonia, Trani, Molfetta, Mola di Bari, Monopoli, Castro, and Gallipoli.
Today Taranto is the world's largest producer of farmed mussels: with 1,300 employees, around 30,000 tons of mussels are processed per year. Mussel farming has characterized the city's economy for centuries, making the mussel the gastronomic symbol of Taranto. It is said that the first mussel gardens in La Spezia, Pula, Olbia and Chioggia were established by mussel farmers who emigrated from this city. The workplace of the Taranto mussel farmers is the boat; every detail of the working method has improved over time.
10 m long structures made of wood or metal, called "pali" (piles), are attached to the seabed, to which ropes and nets are then attached, on which the mussels are grown. The mussels farmed here are particularly tasty and valued because they grow in a special environment, a mixture of salt seawater and karst freshwater. These special environmental conditions of the seas of Taranto are ideal not only for the mussels but also for the fish and crustaceans that find food and shelter between the piles. While there are around 18 submarine freshwater springs, called "Citri", in the Mar Piccolo, there is only one large one in the Mar Grande, which is called "Anello di San Cataldo" in honour of the patron saint of the city."""])
chunks