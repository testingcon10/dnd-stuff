---
aliases: []
tags: [reference]
---

# NPC Relationship Map

A visual map of all known NPCs, their factions, family ties, and connections to the party.

**Legend:**
- Blue nodes = Party members
- Green nodes = Alive NPCs
- Red nodes = Deceased NPCs
- Yellow nodes = Missing NPCs
- Gray nodes = Unknown status
- Solid arrows = Direct relationships
- Dashed arrows = Family connections / party ties
- Purple subgraphs = Faction groupings

```mermaid
graph TD

    %% Style definitions
    classDef alive fill:#2d5016,stroke:#4a8c2a,color:#fff
    classDef dead fill:#5c1a1a,stroke:#8b3a3a,color:#fff
    classDef missing fill:#4a3d00,stroke:#8b7500,color:#fff
    classDef unknown fill:#333,stroke:#666,color:#fff
    classDef party fill:#1a3a5c,stroke:#2a6a9c,color:#fff
    classDef faction fill:#3d1a5c,stroke:#6a2a9c,color:#fff

    %% Party Members
    Netanyahu_D__Kirkuenly["Net"]
    Booker_Locke["Booker"]
    Old_Shell["Old Shell"]
    Cassius_Bellona["Cassius"]
    Ryan_Nigamus["Ryan-Nigamus"]

    %% NPCs
    Amos_the_Storm["Amos the Storm"]
    August["August"]
    Avo_Red["Avo Red"]
    Aya["Aya"]
    Ayla["Ayla"]
    Corso["Corso"]
    Dima["Dima (dead)"]
    Dimitri["Dimitri"]
    Eileen_Whitebeak["Eileen Whitebeak"]
    Ewing["Ewing (missing)"]
    Grig["Grig (dead)"]
    Gwen_Locke["Gwen Locke (missing)"]
    Kay_Dara["Kay'Dara (dead)"]
    Nahara["Nahara"]
    Nath["Nath"]
    Payton_Hightower["Payton Hightower"]
    Sophie["Sophie"]
    Uzog["Uzog"]
    Von["Von"]
    Watkins["Watkins"]

    %% Faction subgraphs
    subgraph Avian_Brotherhood["Avian Brotherhood"]
        Nath
    end

    subgraph Church["Church"]
        Payton_Hightower
    end

    subgraph Elven_Mafia["Elven Mafia"]
        Von
    end

    subgraph Knights_of_Drayik["Knights of Drayik"]
        Avo_Red
    end

    subgraph Senin["Senin"]
        August
        Corso
        Dima
        Eileen_Whitebeak
    end

    subgraph The_Golds["The Golds"]
        Kay_Dara
        Uzog
    end

    %% Relationships
    August -- "Serves under" --> Eileen_Whitebeak
    Avo_Red -- "Founder" --> Knights_of_Drayik
    Aya -- "Father (missing)" --> Ewing
    Aya -- "Close bond (deceased)" --> Grig
    Aya -- "Promised to stop The Golds in exchange for knowledge about poisons" --> Netanyahu_D__Kirkuenly
    Aya -- "Brought Grig's body and gold for a proper burial" --> Cassius_Bellona
    Ayla -- ""Sister" (possibly not by blood)" --> Nahara
    Ayla -- ""Sister" (possibly not by blood)" --> Sophie
    Corso -- "Sister - strained, she opposes his radical approach" --> Eileen_Whitebeak
    Corso -- "Father (deceased) - Corso shares his temperament" --> Dima
    Dima -- "Son - similar temperament" --> Corso
    Dima -- "Daughter" --> Eileen_Whitebeak
    Dimitri -- "Connected" --> Eileen_Whitebeak
    Eileen_Whitebeak -- "Brother - strained relationship due to his radical approach" --> Corso
    Eileen_Whitebeak -- "Father (deceased) - she did not inherit his radical temperament" --> Dima
    Eileen_Whitebeak -- "Aware they are employing the party" --> Church_of_the_Daughter
    Ewing -- "Daughter" --> Aya
    Grig -- "Friend" --> Cassius_Bellona
    Grig -- "Close bond" --> Aya
    Gwen_Locke -- "Twin brother" --> Booker_Locke
    Kay_Dara -- "Lieutenant" --> The_Golds
    Kay_Dara -- "Associate" --> Uzog
    Kay_Dara -- "Associate" --> Nath
    Kay_Dara -- "Associate" --> Von
    Nahara -- ""Sister" (possibly not by blood)" --> Sophie
    Nath -- "Leader" --> Avian_Brotherhood
    Nath -- "Fellow syndicate group" --> The_Golds
    Nath -- "Associate" --> Uzog
    Nath -- "Associate" --> Von
    Payton_Hightower -- "Member" --> The_Church
    Payton_Hightower -- "Friendly contact" --> The_Party
    Sophie -- "Gave his family the path of righteousness" --> Cassius_Bellona
    Uzog -- "Connected" --> The_Golds
    Uzog -- "Associate" --> Von
    Von -- "Leader" --> Elven_Mafia
    Von -- "Fellow syndicate group" --> The_Golds
    Watkins -- "Business arrangement - facilitates their card games for a cut" --> The_Golds

    %% Key party connections
    Netanyahu_D__Kirkuenly -. "Sending Stone contact" .-> Payton_Hightower
    Netanyahu_D__Kirkuenly -. "Poison knowledge deal" .-> Aya
    Booker_Locke -. "Twin - searching for" .-> Gwen_Locke

    %% Apply styles
    class Amos_the_Storm unknown
    class August alive
    class Avo_Red unknown
    class Aya alive
    class Ayla unknown
    class Corso alive
    class Dima dead
    class Dimitri unknown
    class Eileen_Whitebeak alive
    class Ewing missing
    class Grig dead
    class Gwen_Locke missing
    class Kay_Dara dead
    class Nahara unknown
    class Nath alive
    class Payton_Hightower alive
    class Sophie unknown
    class Uzog alive
    class Von alive
    class Watkins alive
    class Netanyahu_D__Kirkuenly party
    class Booker_Locke party
    class Old_Shell party
    class Cassius_Bellona party
    class Ryan_Nigamus party
```

## Faction Summary

| Faction | Members | Status |
|---------|---------|--------|
| [[Avian Brotherhood]] | [[Nath]] (alive) | Active |
| Church | [[Payton Hightower]] (alive) | Active |
| [[Elven Mafia]] | [[Von]] (alive) | Active |
| [[Knights of Drayik]] | [[Avo Red]] (unknown) | Active |
| [[The Senin|Senin]] | [[August]] (alive), [[Corso]] (alive), [[Dima]] (deceased), [[Eileen Whitebeak]] (alive) | Active |
| [[The Golds]] | [[Kay'Dara]] (deceased), [[Uzog]] (alive) | Active |

## Family Trees

### Kenku Bloodline
- [[Dima]] (deceased) - father of [[Corso]] and [[Eileen Whitebeak]]
- [[Corso]] and [[Eileen Whitebeak]] are siblings (strained relationship)

### The Three Sisters
- [[Nahara]], [[Ayla]], [[Sophie]] - possibly not related by blood
- Traveled with a Knight of [[Drayik]] ~150 years ago

### Locke Family
- [[Booker Locke]] and [[Gwen Locke]] are twins
- Parents murdered by [[The Senin|the Senin]], [[Gwen Locke|Gwen]] kidnapped 6 years ago

### Aya's Family
- [[Ewing]] (missing) is [[Aya]]'s father
