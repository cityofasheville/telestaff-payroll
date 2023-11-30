const sql = require('mssql')

const load_one_file = require('./load_one_file');
const getConnection = require('./getConnection');

async function load_db(filelist) {
  const db_connection = await getConnection('munis/munprod/fme_jobs');
  const dbConfig = {
    user: db_connection.username,
    password: db_connection.password,
    database: db_connection.database,
    server: db_connection.host,
    connectionTimeout: 90000,
    requestTimeout: 90000,
    pool: {
      max: 10,
      min: 0,
      idleTimeoutMillis: 90000
    },
    options: {
      encrypt: true, // for azure
      trustServerCertificate: true // change to true for local dev / self-signed certs
    }
  }
  if (db_connection.domain) {
    dbConfig.domain = db_connection.domain;
  }
  // process.stdout.write(JSON.stringify(dbConfig,null,2));
  const depts =
  {
      "Police": {
          tablenm: 'avl.telestaff_import_time_apd',
          sproc: 'avl.sptelestaff_insert_time_apd',
          files: []
      },
      "Fire": {
          tablenm: 'avl.telestaff_import_time',
          sproc: 'avl.sptelestaff_insert_time',
          files: []
      }
  }
  try {
    await sql.connect(dbConfig)
    // categorize files as PD or FD
    filelist.map((filenm) => {
        if (filenm.charAt(0) === "P") {        // Police
            depts.Police.files.push(filenm)
        } else if (filenm.charAt(0) === "F") {  // Fire
            depts.Fire.files.push(filenm)
        }
    })        
    let deptarr = Object.values(depts)

    // Load each of FD/PD: using reduce to call async func sequentially
    const call_load_a_dept = async (previous, dept) => {
        await previous;
        return load_a_dept(sql,dept);
    };
    let dfil = await deptarr.reduce(call_load_a_dept, Promise.resolve())

    sql.close()
    return filelist
  }
  catch (err) {
      console.log("Load DB Error", err);
      throw (err);
  }
}

async function load_a_dept(sql, dept) { // for each of FD/PD, clear table, load all files, run sp
  try {
    if(dept.files.length == 0) return

    await clear_table(sql, dept.tablenm);

    // Load each file: using reduce to call async func sequentially
    const call_load_one_file = async (previous, deptfilenm) => {
        await previous;
        return load_one_file(sql, deptfilenm, dept.tablenm);
    };
    let deptfiles = await dept.files.reduce(call_load_one_file, Promise.resolve())

    await run_stored_proc(sql, dept.sproc);
    
    return
  }
  catch (err) {
      console.log(err);
      throw (err);
  }
}

// async function load_one_file(sql, filenm, tablenm){
//   console.log("load_one_file ",tablenm, "fake: ")
//   return filenm
// }

async function clear_table(sql, tablenm){
  try{
    const result = await sql.query("delete from " + tablenm)

    console.log("Clear table ",tablenm, "Result: ", result.rowsAffected)
  } catch (err){
    console.log(err)
  }
}

async function run_stored_proc(sql, sproc){
  try{
    const result = await sql.query("execute " + sproc)

    console.log("Stored Procedure ", sproc, "Result: ", result.rowsAffected);
  } catch (err){
    console.log(err)
  }
}

module.exports = load_db;
