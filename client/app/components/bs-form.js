import BsForm from 'ember-bootstrap-cp-validations/components/bs-form';
import ObjectProxy from '@ember/object/proxy';
import { Promise } from 'rsvp';
import { computed } from '@ember/object';

export default BsForm.extend(
  {
    hasValidator: computed.notEmpty('model.validate'),
    validate(model) {
      return new Promise(
        (resolve, reject) => {
          let m = model

          if(model instanceof ObjectProxy) {
            m = model.get('content')
          }

          m.validate().then(
            () => model.get(
              'validations.isTruelyValid'
            ) ? resolve() : reject(),
            reject
          )
        }
      )
    }
  }
)
