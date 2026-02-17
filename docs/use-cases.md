# Use Cases
## Coffee Match – Washington Local Coffee Recommendation System
## This is an initial, rougher, and more expansive version of the use cases shown in functional specification

Implicit, vs. explicit, here refers background or secondary systems adjustments that may not be seen by the user or may be summarizing an edge case. "Implicit" sometimes overlaps with "system behavior" in the functional-specification.md.

##---

## Use Case #1A – Users pursue single coffee match

Users: Opt to be matched with single beans

### Initial Selection

 
System Explicit: presents User a question or button for selection
 
Users: express first coffee attribute preference by answering a question (example: decaf or caffeinated?) and/or clicking a respective presented button.
 
System Implicit: narrows the possible coffee bean matches for that user.

### Loop Selection

System Explicit offers the users another question (or filtering option)

System Implicit: There’s more than one coffee bean still available.*
 
Users: Express second coffee attribute preference by answering a question (level of roast for example) and/or clicking a button.
 
-possible repetitions of this cycle – but end when >
 
System:
(Explicit - if there’s one coffee left) the system presents the coffee with other qualitative and quantitative aspects about the coffee.
(Explicit - if prescribed limit to the number of questions - 4? – has been met) the system ranks(Implicit) the remaining coffees and provides the best possible match.
(Implicit - if no questions are left, but there’s multiple coffee matches) the system must rank the remaining coffees and provide the best possible match. 
(Implicit - if no coffees match those preferences) the system must report failure to match or shift to sub-optimal match sequence. (likely akin to taking a step backwards).

System Explicit: The system stops providing questions therefore only allowing backwards or static movements

-System Implicit: there's a logical static or dynamic sequence to the questions or buttons offered the user>

-System Implicit: there's a dynamic ranking of coffee beans occurring>

-System Implicit: there's limit to the number of questions asked of the user, which is at most the number of attributes/features>

##---

## Use Case #1B – Users pursue multiple coffee matches

Users: Opt to be matched with multiple beans
	
System Explicit: presents User a question or button for selection 

### Initial Selection
 
Users: express first coffee attribute preference by answering a question (example: decaf or caffeinated?) and/or clicking a respective presented button.
 
System Implicit: narrows the possible coffee bean matches for that user, keeping track of how many coffees meet this criteria.

System Explicit: If the number of coffee beans meeting this criteria drops below a nominal limit (5?), the system begins to show bean matches and attributes.

System Implicit: There’s more than one coffee bean still available.*

### Loop

System Explicit: offers the users another question (or filtering option)
 
Users: Express second coffee attribute preference by answering a question (level of roast for example) and/or clicking a button.

System Explicit: If the number of coffee beans meeting this criteria drops below a nominal limit (5?), the system shows bean matches and attributes

System Explicit: The system offers the user the ability to step backwards (this might be used in the case where a user moves from 5 coffees down to a single coffee based on the preceding limiting question, and this user wants a smorgasbord of coffees.)

User: The user elects to continue (answer next question) stop, or go backwards, depending upon their preferences
 
-possible repetitions of this cycle – but end when>

(Explicit - if prescribed limit to the number of questions - 4? – has been met but there’s still more than 5 coffees) the system ranks (Implicit) the remaining coffees and provides the best possible match.
(Implicit - if no questions are left, but there’s multiple coffee matches) the system must rank the remaining coffees and provide the best possible match. 
(Implicit - if no coffees match those preferences) the system may report failure to match or shift to sub-optimal match sequence likely akin to stepping backwards.

System Explicit: The system stops providing questions therefore only allowing backwards or static movements

-System Implicit: there's a logical static or dynamic sequence to the questions or buttons offered the user>

-System Implicit: there's a dynamic ranking of coffee beans occurring>

-System Implicit: there's limit to the number of questions asked of the user, which is at most the number of attributes/features>

-Consideration - may add constraint on nominal limit that encourages the handful of beans shown to be from different roasteries*> 

##---

## User #2A Coffee Roastery (New or Existing) wants to add new coffee bean. (opposite case is removal of coffee)

System Explicit: Accepts admin privileges

Admin User: Asks system to add new coffee from a new roastery through some actuation

System Explicit: System requests all required features for that coffee – simultaneously if possible - such as the roastery which it is from, the roasting shade, caffeination, etc, in some sort of entry form.

Admin user: the user elects to continue or stop, based upon whether the required information is at hand.

System Explicit: If the user elects to stop, through some actuation, the requested entry form disappears.

System Explicit: If the user elects to continue, they fill in the cells, and complete by some actuation.

System Implicit: The system checks whether these inputs are valid, and perhaps whether they make sense (are they extreme outliers etc.?)
System Explicit: Now gives the option to provide any optional preexisting fields for the coffee beans (if any other coffees in the system have such a privilege).

Admin user: Either inputs or the elective information and actuates to signify completion, or doesn’t input any information and actuates for completion.

System Explicit: loads the information and perhaps shows a “receipt” summary to the user. 

##---


