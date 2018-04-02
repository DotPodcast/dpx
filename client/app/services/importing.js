import Service, { inject } from '@ember/service';
import config from '../config/environment';
import $ from 'jquery';

export default Service.extend(
  {
    isImporting: false,
    session: inject(),
    start(url) {
      const token = this.get('session.data.authenticated.auth_token')
      return new Promise(
        (resolve, reject) => {
          this.set('isImporting', true)
          $.ajax(
            {
              url: `${config.APP.API_HOST}/api/v1/podcasts/import/`,
              type: 'post',
              dataType: 'json',
              data: JSON.stringify(
                {
                  url: url
                }
              ),
              beforeSend: request => {
                request.setRequestHeader('Content-Type', 'application/json')
                request.setRequestHeader('Authorization', `Bearer ${token}`)
              },
              success: data => {
                this.set('isImporting', false)
                resolve(data.job)
              },
              error: xhr => {
                this.set('isImporting', false)
                reject(xhr)
              }
            }
          )
        }
      )
    }
  }
);
