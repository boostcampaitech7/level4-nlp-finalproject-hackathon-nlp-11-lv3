import api from './api'

function requestQuery(query, max_tokens, temperature, requestQuerySuccess, requestQueryFail) {
    api
        .post('v1/query/', {
            query: query,
            max_tokens: max_tokens,
            temperature: temperature,
        })
        .then(requestQuerySuccess)
        .catch(requestQueryFail);
}

export { requestQuery };