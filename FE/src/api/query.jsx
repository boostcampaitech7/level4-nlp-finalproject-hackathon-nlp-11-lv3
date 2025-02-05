import api from './api'

function requestQuery(query, max_tokens, temperature) {
    api
        .post('vi/query', {
            query: query,
            max_tokens: max_tokens,
            temperature: temperature,
        })
        .then(success)
        .catch(fail);
}

export { requestQuery };