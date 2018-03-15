import BsFormElement from 'ember-bootstrap-cp-validations/components/bs-form/element';
import { computed } from '@ember/object';
import { defineProperty } from '@ember/object';

export default BsFormElement.extend(
  {
    setupValidations() {
      this._super(...arguments)
      defineProperty(
        this,
        'customError',
        computed.readOnly(`model.errors.${this.get('property')}.0.message`)
      )
    }
  }
)
