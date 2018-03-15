import Base from 'ember-simple-auth/authenticators/base';
import config from '../config/environment';
import { inject } from '@ember/service';
import { Promise } from 'rsvp';
import $ from 'jquery';

export default Base.extend(
  {
    cookies: inject(),
    authenticate(username, password) {
      return new Promise(
        (resolve, reject) => {
          $.ajax(
            {
              url: config.APP.API_HOST + '/api/auth/token/create/',
              type: 'POST',
              beforeSend: request => {
                request.setRequestHeader(
                  'X-CSRFToken',
                  this.get('cookies').read('csrftoken')
                )
              },
              data: JSON.stringify(
                {
                  username: username,
                  password: password
                }
              ),
              contentType: 'application/json;charset=utf-8',
              dataType: 'json'
            }
          ).then(
            resolve,
            xhr => {
              reject(
                JSON.parse(xhr.responseText).non_field_errors
              )
            }
          )
        }
      )
    },
    restore(data) {
      return new Promise(
        (resolve, reject) => {
          $.ajax(
            {
              url: '/api/auth/me/',
              type: 'GET',
              beforeSend: request => {
                request.setRequestHeader(
                  'Authorization',
                  `Token ${data.auth_token}`
                )
              },
              ontentType: 'application/json;charset=utf-8',
              dataType: 'json'
            }
          ).then(
            () => {
              resolve(data)
            },
            xhr => {
              reject(
                JSON.parse(xhr.responseText)
              )
            }
          )
        }
      )
    }
  }
);
