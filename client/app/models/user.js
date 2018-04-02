import DS from 'ember-data';
import { validator, buildValidations } from 'ember-cp-validations';

const Validations = buildValidations(
  {
    username: [
      validator('presence', true),
      validator(
        'format',
        {
          regex: /^[a-z0-9]+$/,
          message: 'Usernames may only contain letters and numbers.'
        }
      )
    ],
    email: [
      validator(
        'format',
        {
          type: 'email'
        }
      )
    ],
    password: [
      validator(
        'length',
        {
          min: 7
        }
      )
    ],
    passwordConfirmation: [
      validator(
        'confirmation',
        {
          on: 'password',
          message: '{description} do not match',
          description: 'Passwords'
        }
      )
    ]
  }
)

export default DS.Model.extend(
  Validations,
  {
    username: DS.attr('string'),
    first_name: DS.attr('string'),
    last_name: DS.attr('string'),
    email: DS.attr('string'),
    password: DS.attr('string'),
    passwordConfirmation: DS.attr('string')
  }
)
