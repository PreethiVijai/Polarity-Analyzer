import React, {Component,Fragment} from 'react'
import { getTweets } from './ApiRequests'
import Geocode from "react-geocode";
import { withGoogleMap, GoogleMap, Marker, Circle } from 'react-google-maps';
import bp from './blue_pin.png';
import rp from './red_pin.png';
import gp from './green_pin.png';
import { render } from "react-dom";
import WordCloud from "react-d3-cloud";
import ReactWordcloud from 'react-wordcloud'
import cv from './covid.png'

class PolarityMap extends Component {
  _isMounted = false;
  constructor(props) {
    super(props);
    this.state = {
      tweet_tbl : [],
      latitude:[],
      longitude:[],
      marker:[],
      wordCloud:[]

    }
  }

  componentDidMount() {
    Geocode.setApiKey("AIzaSyCJn2KEsU2i1bdPGqF5pLqxv6dJfys3TXI");
    getTweets().then(res => {
      if (!res.error) {
        console.log("length");
        console.log(res.result[0]);
        let my_sql_dataTable=new Array(res.result.length);
        for(var i =0;i<res.result.length;i++){
            my_sql_dataTable[i]= new Array(4);
          }
        for(i=0;i<res.result.length;i++){

            my_sql_dataTable[i][0]=res.result[i].polarity;
            my_sql_dataTable[i][1]=res.result[i].location;
            my_sql_dataTable[i][2]=res.result[i].id;
            my_sql_dataTable[i][3]=res.result[i].tweets.split(" ");

            this.data(my_sql_dataTable[i][1],my_sql_dataTable[i][2],my_sql_dataTable[i][0]);
            this.state.tweet_tbl.push(my_sql_dataTable);
            

      }
    }
    this.create_word_cloud_data();
   

    })
}
    data(location,id,polarity){
        Geocode.fromAddress(location).then(
            response => {
              const { lat, lng } = response.results[0].geometry.location;
              this.state.latitude.push(lat);
              this.state.longitude.push(lng);
              let marker_arr=new Array(4);
              marker_arr[0]=lat;
              marker_arr[1]=lng;
              marker_arr[2]=id;
              if(polarity===0){
                marker_arr[3]=gp;
              }
              if(polarity===1){
                marker_arr[3]=bp;
              }
              if(polarity===-1){
                marker_arr[3]=rp;
              }
              this.state.marker.push(marker_arr);

            },
            error => {
                var lat=0;
                var lng=0;
                this.state.latitude.push(lat);
              this.state.longitude.push(lng);
              let marker_arr=new Array(4);
              marker_arr[0]=lat;
              marker_arr[1]=lng;
              marker_arr[2]=id;
              if(polarity===0){
                marker_arr[3]=gp;
              }
              if(polarity===1){
                marker_arr[3]=bp;
              }
              if(polarity===-1){
                marker_arr[3]=rp;
              }
              this.state.marker.push(marker_arr);
              console.error("skip");
            }

          );
    }
  
    create_word_cloud_data(){
        let arr_dat = new Array(5*this.state.tweet_tbl.length);
        for(var i =0;i<3;i++){
            for(var j =0;j<this.state.tweet_tbl[i].length;j++){
                let arr = new Array(10);
                arr = this.state.tweet_tbl[i][j][3];

                for(var k = 0;k<arr.length;k++){
                    //console.log(arr[k]);
                    const min = 1;
                    const max = 25;
                    const rand = min + Math.random() * (max - min);
                     arr_dat[i] ={text:arr[k],value:Math.floor(rand)};
                     this.state.wordCloud.push(arr_dat[i]);
                }

            }
        }
        console.log( this.state.wordCloud[10]);
    }


    render() {
        
        const fontSizeMapper = word => Math.log2(word.value) * 5;
        const rotate = word => word.value % 360;
        const GoogleMapExample = withGoogleMap(props => (
            <GoogleMap
              defaultCenter = { { lat: 40.756795, lng: -73.954298 } }
              defaultZoom = { 13 }

            >
                
                {this.state.marker.map(marker => (
                    
    <Marker
      position={{ lat: marker[0], lng: marker[1] }}
      key={marker[2]}
      icon={{
        url: marker[3],
        anchor: new window.google.maps.Point(5, 58),
        scaledSize: new window.google.maps.Size(20, 20)
      }}
      
      
    />
    
))}

          
               
            </GoogleMap>
            
         ));

      return ( 
          <Fragment>
<GoogleMapExample
          containerElement={ <div style={{ height: `1000px`, width: '1000px' }} /> }
          mapElement={ <div style={{ height: `100%` }} /> }
        />

<img src={cv} alt="Logo" />
       


    </Fragment>
        

)
}

}


export default PolarityMap;
