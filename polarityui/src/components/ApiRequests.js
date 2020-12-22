import axios from 'axios'


/*All the get api functions for dashboard*/
export const getTweets = tweet_table => {
  return axios
.get('http://34.121.43.231:8080/tweets', {headers: {
                "Access-Control-Allow-Origin": "*",
            },
          responseType: 'json'
    })
    .then(response => {
      return response.data
    })
    .catch(err => {
      console.log(err)
    })
}

