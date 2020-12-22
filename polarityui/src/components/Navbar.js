import React, { Component, Fragment } from 'react'
import { Link, withRouter } from 'react-router-dom'

class Landing extends Component {
  
  render() {
    const loginRegLink = (
      <ul className="navbar-nav">
        <li className="nav-item">
          <Link to="/Polarity/Covid" className="nav-link">
            Polarity Dashboard
          </Link>
        </li>
 
      </ul>
    )

    

    return (
      <Fragment>
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark rounded">
        <button
          className="navbar-toggler"
          type="button"
          data-toggle="collapse"
          data-target="#navbarsExample10"
          aria-controls="navbarsExample10"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon" />
        </button>

        <div
          className="collapse navbar-collapse justify-content-md-center"
          id="navbarsExample10"
        >
          <ul className="navbar-nav">
            <li className="nav-item">
              <Link to="/" className="nav-link">
                Home
              </Link>
            </li>
          </ul>
          {loginRegLink}
        </div>
      </nav>
      <div style={ribbonStyle} className="jumbotron mt-5">
        <div className="col-sm-8 mx-auto">
          <h1 className="text-center">POLARITY ANALYZER</h1>
        </div>
      </div>
       </Fragment>
    )
  }
}

const ribbonStyle={

    backgroundColor: 'darkgray',
    borderRadius: '50px',
    textAlign: 'center'
  }

export default withRouter(Landing)
