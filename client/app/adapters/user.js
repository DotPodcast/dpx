import ApplicationAdapter from './application';

export default ApplicationAdapter.extend(
  {
    namespace: 'api/auth',
    buildURL(modelName, id, snapshot, requestType, query) {
      var url = this._super(modelName, id, snapshot, requestType, query)

      if(this.get('addTrailingSlashes')) {
        if (url.charAt(url.length - 1) !== '/') {
          url += '/'
        }
      }

      if(requestType === 'createRecord') {
        url += 'create'

        if(this.get('addTrailingSlashes')) {
          url += '/'
        }
      }

      return url
    }
  }
)
