from flask_restx import Api, Resource, fields, marshal_with, reqparse
from database.pokemon_database import Pokemon, db  # Import Pokemon entity from the database module
from pony.orm import db_session, select, commit, PrimaryKey, Required
from enum import Enum

api = Api()

class PokemonType(Enum): #constant
    GRASS = 'grass'
    FIRE = 'fire'
    WATER = 'water'
    ELECTRIC = 'electric'

# Request parser for filtering by type
type_parser = reqparse.RequestParser()                #object is used to define and parse request arguments
type_parser.add_argument('type', type=str, choices=[t.value for t in PokemonType], help='Invalid Pokemon type', required=False)  #specifies that the valid choices for the "type" argument should come from the values of the PokemonType enum.

# Request parser for POST and PATCH
pokemon_parser = reqparse.RequestParser()
pokemon_parser.add_argument("name", type=str, required=True, help="Name cannot be blank")    #request arguments
pokemon_parser.add_argument("type", type=str, choices=[t.value for t in PokemonType], required=True, help="Invalid Pokemon type")
pokemon_parser.add_argument("hp", type=int, required=True, help="HP cannot be blank")

# Define Pokemon model for marshaling
pokemon_model = api.model('Pokemon', {
    'id' : fields.Integer(),
    'name': fields.String(),
    'type': fields.String(),
    'hp': fields.Integer()
})

# Resource for listing and adding Pokemon
@api.route('/pokemon')
class PokemonResource(Resource):


    #GET METHOD 
    @api.expect(type_parser)
    @api.marshal_with(pokemon_model, as_list=True)
    @db_session
    def get(self):
        args = type_parser.parse_args()                                   #parses the arguments passed to the function.we are extracting the type of Pokemon
        pokemon_list = Pokemon.select()                                   #retrieves all the Pokemon
        if args['type']:                                                  
            pokemon_list = pokemon_list.filter(type=args['type'])         #filters the Pokemon list based on the specified type
        result = [p.to_dict() for p in pokemon_list]                      #Convert the QuerySet to a list of dictionaries,dictionary represents a Pokemon and contains its attributes
        return result                                             
          
    
    #POST METHOD - ADD
    @api.expect(pokemon_model)
    @api.marshal_with(pokemon_model, code=201)
    @db_session
    def post(self):
        args = pokemon_parser.parse_args()                                  #line parses the request arguments and retrieves the values for parameters
        name = " ".join(args["name"].split())                               # Remove multiple spaces
        pokemon = Pokemon(name=["name"], type=args["type"], hp=args["hp"])      #ceates a new Pokemon object using the parsed values and assigns it to the "pokemon" variable
        commit()                                                            # Save the new Pokemon to the database
        return pokemon, 201


    #PATCH METHOD - UPDATE
    @api.expect(pokemon_model)
    @api.marshal_with(pokemon_model)
    @db_session
    def patch(self):
        args = pokemon_parser.parse_args()                                  #instance to extract and parse the arguments from the incoming request
        name = " ".join(args["name"].split())                               # Remove multiple spaces
        existing_pokemon = Pokemon.get(id=id)
        if not existing_pokemon:
            return {'message': 'Pokemon not found'}, 404
        existing_pokemon.name = args['name'] 
        existing_pokemon.type = args['type']                                # Update existing Pokemon
        existing_pokemon.hp = args['hp']
        commit()                                                            # Save the changes
        return existing_pokemon























    
  
