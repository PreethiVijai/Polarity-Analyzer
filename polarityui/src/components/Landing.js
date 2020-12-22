import React, { Component } from 'react'

class Landing extends Component {
  render() {
    return (
      <div className="container" >
        <div style = {ribbonStyle} className="jumbotron mt-5">
          <div >
            <h2 className="text-center">A smart tool which estimates the polarity of a given keyword and displays the polarity on a heatmap</h2>
          </div>
        </div>
      </div>
    )
  }
}

const ribbonStyle={
    backgroundColor: 'darkgrey',
    borderRadius: '50px',
    textAlign: 'center'
  }



export default Landing
